#%%
import os
import random
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from PIL import Image
#%%

def get_smallest_dimensions(folder_path, image_files):
    """Find the smallest width and height among a list of images."""
    smallest_width, smallest_height = float('inf'), float('inf')
    for image_file in image_files:
        with Image.open(folder_path + '/' + image_file) as img:
            width, height = img.size
            smallest_width, smallest_height = min(smallest_width, width), min(smallest_height, height)
    return smallest_width, smallest_height
#%%
def resize_image(folder_path, image_path, size):
    """Resize an image to the given size."""
    with Image.open(folder_path + '/' + image_path) as img:
        resized_img = img.resize(size, Image.ANTIALIAS)
        resized_img.save(folder_path + '/' + image_path)
#%%

def apply_effects_composite(clip, effect):
    if effect == 'zoom':
        # Adjusting for a single, centered, and smooth zoom effect
        print('zoom')
        zoom_factor = lambda t: 1 + 0.5 * (t / clip.duration)  # Linear zoom to 150% at the end of the clip
        return clip.resize(zoom_factor)
    elif effect in ['pan_left', 'pan_right']:
        print(f'{effect}')
        pan_clip = clip.resize(lambda t: 1.3)  # Slightly zoom out
        if effect == 'pan_left':
            # Calculate the maximum leftward movement
            max_movement = clip.w * 0.3  # Adjust as needed
            #pan_clip = pan_clip.set_position(lambda t: (max_movement - max_movement * t / clip.duration, 'center'))
            pan_clip = pan_clip.set_position(lambda t: (-max_movement * t / clip.duration, 'center'))
        else:  # pan_right
            # Calculate the maximum rightward movement
            max_movement = clip.w * 0.3  # Adjust as needed
            pan_clip = pan_clip.set_position(lambda t: (max_movement * t / clip.duration - max_movement, 'center'))
        return CompositeVideoClip([pan_clip], size=clip.size)

    elif effect == 'tilt_up':
        print('tilt up')
        pan_clip = clip.resize(lambda t: 1.3)  # Slightly zoom out
        # The initial position should place the bottom of the image at the bottom of the frame
        start_position = -(clip.h * 0.3)  # 30% of the image's height below the frame
        # The movement should end with the top of the image at the top of the frame
        end_position = 0  # Moves the image upwards

        pan_clip = pan_clip.set_position(lambda t: ('center', start_position + (end_position - start_position) * t / clip.duration))

        return CompositeVideoClip([pan_clip], size=clip.size)


    return clip


# %%


def generate_video(folder_path, output_filename="output_video.mp4"):
    # List all image files and sort them alphabetically
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))])

    # Determine the smallest dimensions
    smallest_width, smallest_height = get_smallest_dimensions(folder_path, image_files)

    # Resize images to the smallest dimensions
    #for image_file in image_files:
    #    resize_image(folder_path, image_file, (smallest_width, smallest_height))


    # Find the audio file
    audio_file = next((f for f in os.listdir(folder_path) if f.endswith('.mp3')), None)

    # Load the images and apply random effects
    clips = []
    last_effect = None
    for index, image_file in enumerate(image_files):
        # Load image
        print(index , " image " , image_file)
        img_path = os.path.join(folder_path, image_file)
        clip = ImageClip(img_path, duration=4)  # Start time adjusted for sequential display

        available_effects = ['zoom', 'pan_left', 'pan_right', 'tilt_up']
        if last_effect in available_effects:
            available_effects.remove(last_effect)

        # Choose a random effect and apply it
        effect = random.choice(available_effects)
        clip = apply_effects_composite(clip, effect)  # Apply the chosen effect
        last_effect = effect
        
        clips.append(clip)

    # Concatenate clips sequentially
    final_clip = concatenate_videoclips(clips, method="compose")

    # Add audio if present
    if audio_file:
        audio = AudioFileClip(os.path.join(folder_path, audio_file))
        final_clip = final_clip.set_audio(audio.set_duration(final_clip.duration))

    # Write the result to file
    final_clip.write_videofile(os.path.join(folder_path, output_filename), fps=24)

# %%
# Example usage generate_video('/home/ddy/Downloads/test/video-creator/aaa')
