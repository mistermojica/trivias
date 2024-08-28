from moviepy.editor import concatenate_videoclips, CompositeVideoClip
from moviepy.logger import ProgressBarLogger

class MyBarLogger(ProgressBarLogger):
    def __init__(self, session_uuid, sio):
        super().__init__()
        self.session_uuid = session_uuid
        self.sio = sio

    async def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        percentage = (value / total) * 100 if total > 0 else 0
        await self.sio.emit('video_progress', {'uuid': self.session_uuid, 'progress': percentage})

async def generate_combined_trivia_video(main_question, voice, language, questions_json, background_video_path, background_music_path, logo_path, account_text, tictac_sound_path, ding_sound_path, output_file, question_font_path, options_font_path, account_font_path, question_image_font_path, sessionUUID, sio):
    logger = MyBarLogger(sessionUUID, sio)

    all_clips = []
    target_width, target_height = 1080, 1920
    ctxVideo = {"video_width": target_width, "video_height": target_height}

    for question in questions_json:
        trivia_clip = generate_trivia_video(
            main_question=main_question,
            voice=voice,
            language=language,
            ctxVideo=ctxVideo,
            logo_path=logo_path,
            question_text=question['question_text'],
            question_image=question['question_image'],
            options=question['options'],
            correct_option_index=question['correct_option_index'],
            account_text=account_text,
            narration_text=f"¿{question['question_text']}?",
            narration_text_winner=f"{question['options'][question['correct_option_index']]}!!",
            tictac_sound_path=tictac_sound_path,
            ding_sound_path=ding_sound_path,
            question_font_path=question_font_path,
            options_font_path=options_font_path,
            account_font_path=account_font_path,
            question_image_font_path=question_image_font_path
        )
        all_clips.append(trivia_clip)

    trivia_sequence = concatenate_videoclips(all_clips, method="compose")
    total_duration = trivia_sequence.duration
    background_clip = create_background_video(background_video_path, background_music_path, target_width, target_height, total_duration)
    final_video = CompositeVideoClip([background_clip, trivia_sequence])
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=12, preset='ultrafast', logger=logger)

async def create_video(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, sio):
    trivia = generate_quiz_questions(main_question, num_questions, num_options, language)
    await generate_combined_trivia_video(
        main_question=trivia["main_question"],
        voice=voice,
        language=language,
        questions_json=trivia["questions"],
        background_video_path=f"{SCRIPT_DIR}/public/assets/videos/{background_video}.mp4",
        background_music_path=f"{SCRIPT_DIR}/public/assets/music/{background_music}.mp3",
        logo_path=logo_path or f"{SCRIPT_DIR}/public/assets/images/logo.png",
        account_text=account_text or "@elclubdelosgenios",
        tictac_sound_path=f"{SCRIPT_DIR}/public/assets/audios/clock.mp3",
        ding_sound_path=f"{SCRIPT_DIR}/public/assets/audios/ding.mp3",
        output_file=f"{SCRIPT_DIR}/public/generados/videos/{uuid4}.mp4",
        question_font_path=f"{SCRIPT_DIR}/public/assets/fonts/TT-Milks-Casual-Pie-Trial-Base.otf",
        options_font_path=f"{SCRIPT_DIR}/public/assets/fonts/Sniglet-Regular.ttf",
        account_font_path=f"{SCRIPT_DIR}/public/assets/fonts/Sniglet-Regular.ttf",
        question_image_font_path=f"{SCRIPT_DIR}/public/assets/fonts/AppleColorEmoji.ttf",
        sessionUUID=sessionUUID,
        sio=sio
    )

async def create_video_main(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, sio):
    await sio.emit('greeting', {'uuid': sessionUUID, 'progress': "hola"})
    await create_video(uuid4, language, voice, main_question, num_questions, num_options, background_music, background_video, logo_path, account_text, sessionUUID, sio)