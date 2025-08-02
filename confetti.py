import random
import logging
from tkinter import Canvas, Toplevel
from PIL import Image, ImageDraw, ImageTk

def show_confetti_pil(window, duration=3000, confetti_count=50, animation_speed=20):
    """
    Advanced PIL confetti with rotating pieces, better physics, and fade in/out effects.
    """
    try:
        # Similar setup as above...
        window.update_idletasks()
        if window.winfo_width() <= 1 or window.winfo_height() <= 1:
            return None
        
        overlay = Toplevel(window)
        width = window.winfo_width()
        height = window.winfo_height()
        x_pos = window.winfo_rootx()
        y_pos = window.winfo_rooty()
        
        overlay.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        
        # Start with overlay completely invisible for fade-in effect
        overlay.attributes("-alpha", 0.0)
        
        # Try to make truly transparent
        try:
            overlay.wm_attributes("-transparentcolor", "black")
            canvas_bg = "black"
        except Exception:
            try:
                canvas_bg = "#2b2b2b"  # Use valid color instead of empty string
            except Exception:
                try:
                    canvas_bg = window.cget('bg')
                except Exception:
                    canvas_bg = "#2b2b2b"  # Final fallback
        
        overlay.lift()
        canvas = Canvas(overlay, highlightthickness=0, bg=canvas_bg)
        canvas.pack(fill="both", expand=True)

        # Enhanced confetti with rotation and physics
        confetti_pieces = []
        
        # Animation state variables
        animation_active = True
        frame_count = 0
        fade_in_complete = False
        fade_out_started = False
        current_alpha = 0.0
        target_alpha = 0.8  # Target alpha for normal visibility
        fade_speed = 0.15  # Speed of fade in/out
        
        def fade_in():
            """Gradually fade in the overlay"""
            nonlocal current_alpha, fade_in_complete
            if current_alpha < target_alpha:
                current_alpha = min(current_alpha + fade_speed, target_alpha)
                try:
                    overlay.attributes("-alpha", current_alpha)
                except Exception:
                    pass
                if current_alpha < target_alpha:
                    overlay.after(30, fade_in)  # Continue fading
                else:
                    fade_in_complete = True
            else:
                fade_in_complete = True
        
        def fade_out(callback=None):
            """Gradually fade out the overlay"""
            nonlocal current_alpha, fade_out_started
            fade_out_started = True
            if current_alpha > 0.0:
                current_alpha = max(current_alpha - fade_speed * 2, 0.0)  # Fade out faster
                try:
                    overlay.attributes("-alpha", current_alpha)
                except Exception:
                    pass
                if current_alpha > 0.0:
                    overlay.after(20, lambda: fade_out(callback))  # Continue fading
                else:
                    if callback:
                        callback()
            else:
                if callback:
                    callback()
        
        def create_rotating_confetti(size, color):
            """Create multiple rotated versions of confetti for smooth rotation"""
            frames = []
            for angle in range(0, 360, 15):  # 24 frames for full rotation
                img = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Create rotated rectangle
                center = size
                half_size = size // 2
                
                # Calculate rotated corners
                import math
                rad = math.radians(angle)
                cos_a, sin_a = math.cos(rad), math.sin(rad)
                
                corners = [
                    (-half_size, -half_size//2),
                    (half_size, -half_size//2),
                    (half_size, half_size//2),
                    (-half_size, half_size//2)
                ]
                
                rotated_corners = []
                for x, y in corners:
                    new_x = center + x * cos_a - y * sin_a
                    new_y = center + x * sin_a + y * cos_a
                    rotated_corners.append((new_x, new_y))
                
                draw.polygon(rotated_corners, fill=color, outline=None)
                frames.append(ImageTk.PhotoImage(img))
            
            return frames

        # Generate advanced confetti
        for _ in range(confetti_count):
            x = random.randint(0, width)
            y = random.randint(-100, -10)
            size = random.randint(8, 20)
            color = random.choice([
                "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", 
                "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
                "#FFD93D", "#6BCF7F", "#FF8A80", "#B39DDB", "#81D4FA"
            ])
            
            # Create rotation frames
            rotation_frames = create_rotating_confetti(size, color)
            
            # Add to canvas with first frame
            canvas_item = canvas.create_image(x, y, image=rotation_frames[0], anchor="nw")
            
            confetti_pieces.append({
                'canvas_item': canvas_item,
                'frames': rotation_frames,
                'current_frame': 0,
                'speed_y': random.uniform(2.0, 5.0),
                'speed_x': random.uniform(-1.0, 1.0),
                'rotation_speed': random.randint(1, 3),
                'gravity': random.uniform(0.02, 0.05),
                'wind': random.uniform(-0.1, 0.1),
                'size': size
            })

        animation_active = True
        frame_count = 0

        def animate_advanced():
            nonlocal animation_active, frame_count
            if not animation_active:
                return
                
            try:
                # Only animate confetti if fade-in is complete
                if fade_in_complete and not fade_out_started:
                    for piece in confetti_pieces:
                        canvas_item = piece['canvas_item']
                        
                        # Physics simulation
                        piece['speed_y'] += piece['gravity']  # Gravity
                        piece['speed_x'] += piece['wind']    # Wind effect
                        
                        # Move confetti
                        canvas.move(canvas_item, piece['speed_x'], piece['speed_y'])
                        
                        # Rotate confetti (change frame every few animation steps)
                        if frame_count % piece['rotation_speed'] == 0:
                            piece['current_frame'] = (piece['current_frame'] + 1) % len(piece['frames'])
                            canvas.itemconfig(canvas_item, image=piece['frames'][piece['current_frame']])
                        
                        # Check bounds and reset
                        coords = canvas.coords(canvas_item)
                        if len(coords) >= 2:
                            x, y = coords[0], coords[1]
                            
                            if y > height + 50 or x < -50 or x > width + 50:
                                # Reset confetti piece
                                new_x = random.randint(0, width)
                                new_y = random.randint(-100, -10)
                                canvas.coords(canvas_item, new_x, new_y)
                                piece['speed_y'] = random.uniform(2.0, 5.0)
                                piece['speed_x'] = random.uniform(-1.0, 1.0)
                
                frame_count += 1
                
                if animation_active:
                    overlay.after(animation_speed, animate_advanced)
                    
            except Exception as e:
                logging.debug(f"Advanced animation error: {e}")
                animation_active = False

        def close_overlay_advanced():
            nonlocal animation_active
            animation_active = False
            
            def cleanup():
                try:
                    # Clean up all image references
                    for piece in confetti_pieces:
                        piece['frames'].clear()
                    overlay.destroy()
                except Exception as e:
                    logging.debug(f"Error closing advanced confetti overlay: {e}")
            
            # Start fade out with cleanup callback
            fade_out(cleanup)

        def close_overlay_immediate():
            """Close overlay immediately (for click events)"""
            nonlocal animation_active
            if not fade_out_started:  # Only allow immediate close if not already fading out
                animation_active = False
                fade_out(lambda: overlay.destroy())
        
        # Start fade-in effect
        fade_in()
        
        # Start animation
        animate_advanced()
        
        # Schedule automatic cleanup with fade-out
        window.after(duration - 500, close_overlay_advanced)  # Start fade-out 500ms before end
        
        # Allow manual closing by clicking on overlay
        overlay.bind("<Button-1>", lambda e: close_overlay_immediate())
        
        logging.debug("Advanced PIL Confetti animation started")
        return overlay
        
    except Exception as e:
        logging.error(f"Failed to create advanced PIL confetti animation: {e}")
        return None
