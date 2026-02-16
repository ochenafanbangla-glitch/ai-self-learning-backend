class MartingaleRecovery:
    def __init__(self, base_bet=10, max_steps=5, confidence_threshold=0.85):
        self.base_bet = base_bet
        self.max_steps = max_steps
        self.confidence_threshold = confidence_threshold
        self.current_step = 0
        self.total_loss = 0

    def get_bet_strategy(self, confidence):
        """
        Returns the recommended bet amount and whether to signal.
        Only signals if confidence is high enough during recovery.
        """
        if self.total_loss == 0:
            return self.base_bet, True # Normal bet
        
        if self.current_step >= self.max_steps:
            # Reset if max steps reached to prevent total bankruptcy
            self.reset()
            return self.base_bet, True

        # Calculate recovery bet: (Total Loss + Base Bet)
        # Assuming 1:1 payout for simplicity
        recovery_bet = self.total_loss + self.base_bet
        
        # Only signal if confidence is high
        should_signal = confidence >= self.confidence_threshold
        
        return recovery_bet, should_signal

    def update_result(self, won, bet_amount):
        if won:
            self.reset()
        else:
            self.total_loss += bet_amount
            self.current_step += 1

    def reset(self):
        self.total_loss = 0
        self.current_step = 0

# Example usage:
# recovery = MartingaleRecovery()
# bet, signal = recovery.get_bet_strategy(0.9)
# recovery.update_result(False, bet)
