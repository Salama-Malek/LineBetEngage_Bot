from apscheduler.schedulers.background import BackgroundScheduler

# Weekly performance summary function
def send_weekly_summary(context):
    """
    Sends a weekly performance summary to the designated group chat.
    """
    try:
        context.bot.send_message(
            chat_id=-1002325909184,  # Replace with your group chat ID
            text=(
                "📊 *Weekly Performance Summary:*\n\n"
                "👥 *Total Players Referred:* 50\n"
                "💰 *Total Commission Earned:* $1,200\n\n"
                "🚀 Keep up the great work! Contact us for more tips to improve performance."
            ),
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error in sending weekly summary: {e}")

# Scheduler function to schedule tasks
def schedule_weekly_summary(bot):
    """
    Sets up the scheduler to send weekly performance summaries.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_weekly_summary,
        trigger='interval',
        weeks=1,  # Set the interval for weekly updates
        kwargs={'context': bot}  # Pass the bot context to the job
    )
    scheduler.start()
