class Attendance:
    """
    Tracks all-time and current chatters for the session.
    """
    def __init__(self):
        self.all_time_chatters = set()
        self.current_chatters = set()

    def on_join(self, user_name: str):
        self.current_chatters.add(user_name)
        self.all_time_chatters.add(user_name)

    def on_leave(self, user_name: str):
        self.current_chatters.discard(user_name)

    def is_current(self, user_name: str) -> bool:
        return user_name in self.current_chatters

    def is_all_time(self, user_name: str) -> bool:
        return user_name in self.all_time_chatters

    def get_current_list(self):
        return list(self.current_chatters)

    def get_all_time_list(self):
        return list(self.all_time_chatters)

    def current_count(self):
        return len(self.current_chatters)

    def all_time_count(self):
        return len(self.all_time_chatters)
