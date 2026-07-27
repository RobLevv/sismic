class Stopwatch:
    def __init__(self) -> None:
        self.elapsed_time = 0
        self.split_time = 0
        self.is_split = False
        self.running = False

    def start(self) -> None:
        # Start internal timer
        self.running = True

    def stop(self) -> None:
        # Stop internal timer
        self.running = False

    def reset(self) -> None:
        # Reset internal timer
        self.elapsed_time = 0

    def split(self) -> None:
        # Split time
        if not self.is_split:
            self.is_split = True
            self.split_time = self.elapsed_time

    def unsplit(self) -> None:
        # Unsplit time
        if self.is_split:
            self.is_split = False

    def display(self):
        # Return the value to display
        if self.is_split:
            return int(self.split_time)
        return int(self.elapsed_time)

    def update(self, delta) -> None:
        # Update internal timer of ``delta`` seconds
        if self.running:
            self.elapsed_time += delta
