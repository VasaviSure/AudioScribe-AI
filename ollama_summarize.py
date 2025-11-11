import ollama

def summarize_transcript(transcript_file="the_audio_whisper.txt", output_file="meeting_summary.txt"):
    """
    Summarize transcript using Ollama and return the summary text
    """
    # Load your transcript
    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript = f.read()

    # Prepare the prompt
    prompt = (
        "Analyze this meeting transcript and provide a comprehensive summary with the following sections:\n\n"
        "1. EXECUTIVE SUMMARY: Brief overview of the meeting\n"
        "2. KEY DECISIONS MADE: Important decisions and outcomes\n"
        "3. ACTION ITEMS: Specific tasks that need to be completed\n"
        "4. TASK ASSIGNMENTS: For each task, specify WHO was assigned WHAT task and any deadlines mentioned\n"
        "5. IMPORTANT DISCUSSION POINTS: Key topics and concerns raised\n\n"
        "For task assignments, be very specific about:\n"
        "- Who is responsible for each task\n"
        "- What exactly needs to be done\n"
        "- Any mentioned deadlines or timelines\n"
        "- Any dependencies or requirements\n\n"
        "Meeting Transcript:\n\n" + transcript
    )

    # Run Ollama chat with smaller model for lower memory usage
    # Using llama3.2:1b (1.3GB) instead of llama3 (4.7GB)
    response = ollama.chat(model='llama3.2:1b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    summary_text = response['message']['content']

    # Save the summary and action items
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Summary and action items saved to {output_file}")
    return summary_text

if __name__ == "__main__":
    # This code only runs when the script is executed directly
    summarize_transcript()
