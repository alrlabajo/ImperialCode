#######################################
# ERRORS
#######################################

def string_with_arrows(text, pos_start, pos_end):
        result = ''

        # Calculate indices
        idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

        # Generate each line
        line_count = pos_end.ln - pos_start.ln + 1
        for i in range(line_count):
            # Calculate line columns
            line = text[idx_start:idx_end]
            col_start = pos_start.col if i == 0 else 0
            col_end = pos_end.col if i == line_count - 1 else len(line) - 1

            # Append to result
            result += line + '\n'
            result += ' ' * col_start + '^' * (col_end - col_start)

            # Re-calculate indices
            idx_start = idx_end
            idx_end = text.find('\n', idx_start + 1)
            if idx_end < 0: idx_end = len(text)

        return result.replace('\t', '')

class Error(Exception):
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f"{self.error_name}: {self.details}\n"
        
        # More robust position handling
        try:
            if self.pos_start and hasattr(self.pos_start, 'fn'):
                # Standard position object with filename and line number
                result += f"File {self.pos_start.fn}, line {self.pos_start.ln + 1}\n\n"
                
                # Get the line content if available
                if hasattr(self.pos_start, 'ftxt'):
                    line = self.pos_start.ftxt.split('\n')[self.pos_start.ln]
                    result += line + '\n'
                    
                    # Calculate error pointer position
                    col_start = self.pos_start.col
                    
                    # Add the error pointer
                    result += ' ' * col_start + '^'
            elif self.pos_start and isinstance(self.pos_start, list):
                # Handle list format position [type, filename, line, column]
                if len(self.pos_start) >= 4:
                    result += f"File {self.pos_start[1]}, line {self.pos_start[2]}\n\n"
                    # Cannot show line content in this case
            else:
                # Fallback for other position types
                result += f"At position: {self.pos_start}\n"
        except Exception as e:
            # Last resort fallback if position handling fails
            result += f"(Error details unavailable: {str(e)})\n"
            
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class IllegalKeyword(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Keyword', details)

class IdentifierLimitError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Identifier Limit Exceeded', details)

class IllegalDelimiter(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Delimiter', details)

class ExceedNumeralError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Exceed Numeral', details)

class ExceedDecimalError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Exceed Decimal', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)
