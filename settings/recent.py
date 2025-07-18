"""
Recent Projects Manager for QuickEDL
Handles the list of recently opened projects.
"""

import json
import logging
from pathlib import Path
from typing import List, Callable
import ttkbootstrap as ttk


class RecentProjectsManager:
    """Manages the list of recently opened projects."""
    
    def __init__(self, settings_manager, max_recent: int = 10):
        """
        Initialize the recent projects manager.
        
        Args:
            settings_manager: The settings manager instance
            max_recent: Maximum number of recent projects to keep
        """
        self.settings_manager = settings_manager
        self.max_recent = max_recent
        self.recent_file = None
        self._init_recent_file()
    
    def _init_recent_file(self):
        """Initialize the recent projects file path."""
        try:
            settings_folder = self.settings_manager.get_settings_folder_path()
            if settings_folder and settings_folder.exists():
                self.recent_file = settings_folder / "recent_projects.json"
                logging.debug(f"Recent projects file: {self.recent_file}")
            else:
                logging.debug("Settings folder not found, recent projects disabled")
                self.recent_file = None
        except Exception as e:
            logging.error(f"Error initializing recent projects file: {e}")
            self.recent_file = None
    
    def is_available(self) -> bool:
        """Check if recent projects feature is available."""
        return self.recent_file is not None
    
    def load_recent_projects(self) -> List[dict]:
        """
        Load the list of recent projects from file.
        
        Returns:
            List of project dictionaries with 'name' and 'path' keys
        """
        if not self.is_available():
            return []
        
        try:
            if self.recent_file.exists():
                with self.recent_file.open('r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validate structure
                    if isinstance(data, list):
                        # Filter out invalid entries
                        valid_projects = []
                        for item in data:
                            if (isinstance(item, dict) and 
                                'name' in item and 
                                'path' in item and
                                isinstance(item['name'], str) and
                                isinstance(item['path'], str)):
                                valid_projects.append(item)
                        return valid_projects
            return []
        except Exception as e:
            logging.error(f"Error loading recent projects: {e}")
            return []
    
    def save_recent_projects(self, projects: List[dict]):
        """
        Save the list of recent projects to file.
        
        Args:
            projects: List of project dictionaries
        """
        if not self.is_available():
            return
        
        try:
            # Ensure parent directory exists
            self.recent_file.parent.mkdir(parents=True, exist_ok=True)
            
            with self.recent_file.open('w', encoding='utf-8') as f:
                json.dump(projects, f, indent=2, ensure_ascii=False)
            logging.debug(f"Saved {len(projects)} recent projects")
        except Exception as e:
            logging.error(f"Error saving recent projects: {e}")
    
    def add_project(self, project_name: str, project_path: str):
        """
        Add a project to the recent projects list.
        
        Args:
            project_name: Name of the project
            project_path: Path to the project file
        """
        if not self.is_available() or not project_name or not project_path:
            return
        
        try:
            projects = self.load_recent_projects()
            
            # Create new project entry
            new_project = {
                'name': project_name,
                'path': str(Path(project_path).resolve())
            }
            
            # Remove existing entry if it exists (to move it to top)
            projects = [p for p in projects if p.get('path') != new_project['path']]
            
            # Add to beginning of list
            projects.insert(0, new_project)
            
            # Limit to max_recent entries
            if len(projects) > self.max_recent:
                projects = projects[:self.max_recent]
            
            self.save_recent_projects(projects)
            logging.info(f"Added project to recent list: {project_name}")
            
        except Exception as e:
            logging.error(f"Error adding project to recent list: {e}")
    
    def remove_project(self, project_path: str):
        """
        Remove a project from the recent projects list.
        
        Args:
            project_path: Path to the project file to remove
        """
        if not self.is_available():
            return
        
        try:
            projects = self.load_recent_projects()
            project_path_resolved = str(Path(project_path).resolve())
            
            # Remove the project
            projects = [p for p in projects if p.get('path') != project_path_resolved]
            
            self.save_recent_projects(projects)
            logging.info(f"Removed project from recent list: {project_path}")
            
        except Exception as e:
            logging.error(f"Error removing project from recent list: {e}")
    
    def update_max_recent(self, new_max: int):
        """
        Update the maximum number of recent projects.
        
        Args:
            new_max: New maximum number of recent projects
        """
        self.max_recent = new_max
        
        # Trim existing list if necessary
        if self.is_available():
            projects = self.load_recent_projects()
            if len(projects) > new_max:
                projects = projects[:new_max]
                self.save_recent_projects(projects)


class RecentProjectsMenu:
    """Manages the recent projects submenu in the GUI."""
    
    def __init__(self, parent_menu, recent_manager: RecentProjectsManager, 
                 load_project_callback: Callable[[str], None]):
        """
        Initialize the recent projects menu.
        
        Args:
            parent_menu: The parent menu to attach the submenu to
            recent_manager: The recent projects manager instance
            load_project_callback: Callback function to load a project
        """
        self.parent_menu = parent_menu
        self.recent_manager = recent_manager
        self.load_project_callback = load_project_callback
        self.submenu = None
        self.separator_index = None
        
    def create_submenu(self):
        """Create and populate the recent projects submenu."""
        if not self.recent_manager.is_available():
            return
        
        try:
            # Create submenu
            self.submenu = ttk.Menu(self.parent_menu, tearoff=0)
            
            # Add separator before recent projects menu
            self.separator_index = self.parent_menu.index('end') + 1
            self.parent_menu.add_separator()
            
            # Add submenu to parent
            self.parent_menu.add_cascade(label="Recent Projects", menu=self.submenu)
            
            # Populate submenu
            self.update_submenu()
            
        except Exception as e:
            logging.error(f"Error creating recent projects submenu: {e}")
    
    def update_submenu(self):
        """Update the recent projects submenu with current projects."""
        if not self.submenu or not self.recent_manager.is_available():
            return
        
        try:
            # Clear existing entries
            self.submenu.delete(0, 'end')
            
            # Load recent projects
            projects = self.recent_manager.load_recent_projects()
            
            if projects:
                for project in projects:
                    project_name = project.get('name', 'Unknown')
                    project_path = project.get('path', '')
                    
                    # Truncate long names for display
                    display_name = project_name
                    if len(display_name) > 30:
                        display_name = display_name[:27] + "..."
                    
                    self.submenu.add_command(
                        label=display_name,
                        command=lambda path=project_path: self._load_recent_project(path)
                    )
            else:
                # Show "No recent projects" when list is empty
                self.submenu.add_command(
                    label="No recent projects",
                    state='disabled'
                )
                
        except Exception as e:
            logging.error(f"Error updating recent projects submenu: {e}")
    
    def _load_recent_project(self, project_path: str):
        """
        Load a recent project and handle errors.
        
        Args:
            project_path: Path to the project folder
        """
        try:
            # Check if project folder still exists
            if not Path(project_path).exists():
                # Show error message
                from ttkbootstrap.dialogs import Messagebox
                Messagebox.show_error(
                    title="Project not found",
                    message=f"The project folder could not be found:\n{project_path}\n\nIt will be removed from the recent projects list."
                )
                
                # Remove from recent projects
                self.recent_manager.remove_project(project_path)
                
                # Update submenu
                self.update_submenu()
                return
            
            # Load the project
            self.load_project_callback(project_path)
            
        except Exception as e:
            logging.error(f"Error loading recent project {project_path}: {e}")
            from ttkbootstrap.dialogs import Messagebox
            Messagebox.show_error(
                title="Error loading project",
                message=f"An error occurred while loading the project:\n{str(e)}"
            )
