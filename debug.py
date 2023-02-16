import arrow
import chardet
import codecs

class Debug():
    summary = []
    full_log = []
    successful = []


    def __init__(self, filename:str) -> None:
        """Input filename, do not include extension. Its already `.txt` by default"""
        now = arrow.utcnow().to('local').datetime
        formatted_now = now.strftime('%m_%d_%y %I_%M_%S %p')
        self.text_file = f'{filename} - {formatted_now}.txt'
        self.start_time = arrow.utcnow() # Initialize script time.
        # Creating room for summary
    
    def end(self) -> None:
        print('Summarizing...')
        self.end_time = arrow.utcnow()
        elapsed = self.get_elapsed_time(self.start_time,self.end_time)
        self.is_summary(f'Script total runtime elapsed: {elapsed}')
        self.print(f'Script total runtime elapsed: {elapsed}')
        self.summarize()
        print('Script Ended!')

    def write(self, message: str) -> None:
        """Writes into text file."""
        if not isinstance(message, bytes):
            message = message.encode()
        encoding = chardet.detect(message)['encoding']
        if encoding and encoding.lower() != 'utf-8':
            message = message.decode(encoding).encode('utf-8')
        with open(self.text_file, 'ab') as f:
            f.write(message)

    def is_successful(self, message:str) -> None:
        """Append to successful"""
        self.successful.append(message)

    def is_summary(self,message:str) -> None:
        """Append to summary"""
        self.summary.append(message)

    def summarize(self) -> None:
        """Write summary and full log to the beginning of the text file."""
        if len(self.summary):
            with open(self.text_file, 'r+',encoding='utf-8') as f:
                summary_str = '\n'.join(str(s) for s in self.summary)
                full_str = f.read()
                f.seek(0)
                f.write(f'Summary:\n{summary_str}\n\nFull log:\n{"-" * 50}\n{full_str}')

    def print(self, message:str) -> None:
        """Prints to terminal, then append write to text file."""
        self.write(message + '\n')
        # self.full_log.append(message + '\n')
        print(message)
    
    def get_elapsed_time(self, started:arrow.Arrow, ended:arrow.Arrow) -> str:
        """Returns a duration from two time period eg. 0h:0m:0s"""
        elapsed_time = ended - started
        print(elapsed_time.total_seconds())
        hours, minutes, seconds = self.format_time(elapsed_time.total_seconds())
        if hours:
            return f'{hours}h:{minutes}m:{seconds}s'
        if not hours and minutes:
            return f'{minutes}m:{seconds}s'
        if not hours and not minutes:
            return f'{seconds}s'
        
    def format_time(self,seconds) -> tuple:
        """ Returns a tuple of hours,minutes,seconds"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return hours, minutes, seconds
