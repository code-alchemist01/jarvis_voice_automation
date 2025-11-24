"""
Notification system for JARVIS
"""
import platform

# Try to import Windows toast notifications
WIN10TOAST_AVAILABLE = False
try:
    from win10toast import ToastNotifier
    WIN10TOAST_AVAILABLE = True
except ImportError:
    pass  # win10toast not available


def show_notification(title, message, duration=5):
    """Show a system notification"""
    try:
        if platform.system() == 'Windows' and WIN10TOAST_AVAILABLE:
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                duration=duration,
                threaded=True
            )
            return True
        else:
            # Fallback: print to console
            print(f"[{title}] {message}")
            return True
    except Exception as e:
        print(f"Error showing notification: {e}")
        return False


def show_reminder_notification(message):
    """Show a reminder notification"""
    return show_notification("JARVIS Hatırlatıcı", message, duration=10)


def show_error_notification(message):
    """Show an error notification"""
    return show_notification("JARVIS Hata", message, duration=5)


def show_success_notification(message):
    """Show a success notification"""
    return show_notification("JARVIS", message, duration=3)

