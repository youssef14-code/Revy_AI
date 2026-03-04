from langchain_core.tools import tool
from Agent_Builder.services import BookingService, MemoryService

def create_booking_tool(user):  # ← رجّع user هنا
    
    @tool
    def book_appointment(
        day: str,        # ← بدل appointment_date
        time: str,       # ← ضيف time
        phone_number: str,
        description: str = ""  # ← بدل service_name
    ) -> dict:
        """
        Book a business appointment or meeting for a client.
        Only call this tool when you have all required fields AND client confirms.
        Fields needed: day, time, phone_number, and optionally description (e.g. 'AI Agent consultation', 'Business meeting').
        """
        result = BookingService.book(
            user=user,         # ← ضيف user
            day=day,
            time=time,
            phone_number=phone_number,
            description=description
        )

        if result:
            return {
                "status": "success",
                "message": f"✅ تم الحجز ليوم {day} الساعة {time}",
            }
        else:
            return {
                "status": "error",
                "message": "❌ فشل الحجز في قاعدة البيانات"
            }

    return book_appointment