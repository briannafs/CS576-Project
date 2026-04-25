class MailboxMonitor:
    def __init__(self, threshold=50):
        self.threshold = threshold
        self.has_mail = False

    def detect(self, weight):
        if weight is None:
            return False
        return weight > self.threshold

    def update(self, weight):
        detected = self.detect(weight)

        # Mail arrives
        if not self.has_mail and detected:
            self.has_mail = True
            return "MAIL_ARRIVED"

        # Mail removed
        if self.has_mail and not detected:
            self.has_mail = False
            return "MAIL_REMOVED"

        return None