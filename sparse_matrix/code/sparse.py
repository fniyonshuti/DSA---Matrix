import os
import re  # Ensure the re module is imported

class CompressedMatrix:
    """
    Represents a compressed matrix with operations for addition, subtraction, multiplication, 
    loading from file, and saving to file.
    """

    def __init__(self, row_count, column_count):
        self.row_count = row_count
        self.column_count = column_count
        self.non_zero_elements = {}  # Initialize the dictionary for non-zero elements

    @classmethod
    def load_from_file(cls, file_path):
        """
        Loads a CompressedMatrix from a specified file.

        :param file_path: The path to the matrix file.
        :return: An instance of CompressedMatrix.
        """
        lines = cls._read_file(file_path)
        total_rows, total_cols = cls._parse_dimensions(lines)

        matrix_instance = cls(total_rows, total_cols)
        cls._parse_non_zero_elements(lines, matrix_instance)

        return matrix_instance

    @staticmethod
    def _read_file(file_path):
        """
        Reads the contents of a file.

        :param file_path: The path to the file.
        :return: List of lines from the file.
        """
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
            if len(lines) < 2:
                raise ValueError(f"File {file_path} does not contain enough lines for matrix dimensions.")
            return lines
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}.")

    @classmethod
    def _parse_dimensions(cls, lines):
        """
        Parses the dimensions of the matrix from the file lines.

        :param lines: List of lines from the matrix file.
        :return: Tuple containing the total rows and columns.
        """
        row_pattern = re.match(r'rows=(\d+)', lines[0].strip())
        col_pattern = re.match(r'cols=(\d+)', lines[1].strip())

        if not row_pattern or not col_pattern:
            raise ValueError(f"Invalid dimension format in file. Expected 'rows=X' and 'cols=Y'.")

        return int(row_pattern[1]), int(col_pattern[1])

    @classmethod
    def _parse_non_zero_elements(cls, lines, matrix_instance):
        """
        Parses non-zero elements from the file lines and adds them to the matrix instance.

        :param lines: List of lines from the matrix file.
        :param matrix_instance: The CompressedMatrix instance to populate.
        """
        for i in range(2, len(lines)):
            line = lines[i].strip()
            if not line:  # Skip empty lines
                continue

            match = re.match(r'\((\d+),\s*(\d+),\s*(-?\d+)\)', line)
            if not match:
                raise ValueError(f"Invalid format at line {i + 1}: {line}.")

            row_index = int(match[1])
            col_index = int(match[2])
            value = int(match[3])
            matrix_instance.set_value(row_index, col_index, value)

    def get_value(self, row_index, col_index):
        """
        Retrieves the value of an element at a specific row and column.

        :param row_index: The row index of the element.
        :param col_index: The column index of the element.
        :return: The value at the specified position, or 0 if not set.
        """
        return self.non_zero_elements.get((row_index, col_index), 0)  # Return the value or 0 if not found

    def set_value(self, row_index, col_index, value):
        """
        Sets the value of an element at a specific row and column.

        :param row_index: The row index where the value should be set.
        :param col_index: The column index where the value should be set.
        :param value: The value to set at the specified position.
        """
        self.row_count = max(self.row_count, row_index + 1)  # Update row count if needed
        self.column_count = max(self.column_count, col_index + 1)  # Update column count if needed
        self.non_zero_elements[(row_index, col_index)] = value  # Set the value in the dictionary

    def add(self, other_matrix):
        """
        Adds two compressed matrices.

        :param other_matrix: The other CompressedMatrix to add.
        :return: A new CompressedMatrix that is the sum of the two matrices.
        """
        self._check_dimensions(other_matrix, "addition")
        result_matrix = self._create_empty_matrix()

        self._copy_non_zero_elements(result_matrix)  # Copy elements from self

        # Add elements from the other matrix
        for (row_index, col_index), value in other_matrix.non_zero_elements.items():
            current_value = result_matrix.get_value(row_index, col_index)
            result_matrix.set_value(row_index, col_index, current_value + value)

        return result_matrix

    def subtract(self, other_matrix):
        """
        Subtracts one compressed matrix from another.

        :param other_matrix: The other CompressedMatrix to subtract.
        :return: A new CompressedMatrix that is the result of the subtraction.
        """
        self._check_dimensions(other_matrix, "subtraction")
        result_matrix = self._create_empty_matrix()

        self._copy_non_zero_elements(result_matrix)  # Copy elements from self

        # Subtract elements from the other matrix
        for (row_index, col_index), value in other_matrix.non_zero_elements.items():
            current_value = result_matrix.get_value(row_index, col_index)
            result_matrix.set_value(row_index, col_index, current_value - value)

        return result_matrix

    def multiply(self, other_matrix):
        """
        Multiplies two compressed matrices.

        :param other_matrix: The other CompressedMatrix to multiply.
        :return: A new CompressedMatrix that is the product of the two matrices.
        """
        if self.column_count != other_matrix.row_count:
            raise ValueError("Number of columns of the first matrix must equal the number of rows of the second matrix.")

        result_matrix = CompressedMatrix(self.row_count, other_matrix.column_count)

        # Multiply matrices
        for (row_index, col_index), value in self.non_zero_elements.items():
            for k in range(other_matrix.column_count):
                other_value = other_matrix.get_value(col_index, k)
                if other_value != 0:
                    current_value = result_matrix.get_value(row_index, k)
                    result_matrix.set_value(row_index, k, current_value + value * other_value)

        return result_matrix

    def _check_dimensions(self, other_matrix, operation):
        """
        Checks if the dimensions of the matrices are compatible for the specified operation.

        :param other_matrix: The other CompressedMatrix to compare dimensions with.
        :param operation: The operation being performed (addition or subtraction).
        """
        if self.row_count != other_matrix.row_count or self.column_count != other_matrix.column_count:
            raise ValueError(f"Matrices must have the same dimensions for {operation}.")

    def _create_empty_matrix(self):
        """
        Creates an empty CompressedMatrix with the same dimensions.

        :return: A new CompressedMatrix instance with the same dimensions.
        """
        return CompressedMatrix(self.row_count, self.column_count)

    def _copy_non_zero_elements(self, target_matrix):
        """
        Copies non-zero elements to another CompressedMatrix.

        :param target_matrix: The CompressedMatrix to copy elements into.
        """
        for (row_index, col_index), value in self.non_zero_elements.items():
            target_matrix.set_value(row_index, col_index, value)

    def __str__(self):
        """
        Converts the CompressedMatrix to a string representation.

        :return: The string representation of the CompressedMatrix.
        """
        result = f"rows={self.row_count}\ncols={self.column_count}\n"
        for (row_index, col_index), value in self.non_zero_elements.items():
            result += f"({row_index}, {col_index}, {value})\n"
        return result.strip()  # Return trimmed string

    def save_to_file(self, file_path):
        """
        Saves the CompressedMatrix to a file.

        :param file_path: The path to save the matrix file.
        """
        content = str(self)  # Get string representation
        with open(file_path, "w") as file:
            file.write(content)  # Write to file

def execute_calculations():
    """
    Performs matrix operations based on user input.
    """
    try:
        matrix_operations = {
            '1': {"name": "multiplication", "method": "multiply"},
            '2': {"name": "subtraction", "method": "subtract"},
            '3': {"name": "addition", "method": "add"},
        }

        # Display the operations menu
        print("Choose operations:")
        for key, operation in matrix_operations.items():
            print(f"{key}: {operation['name']}")

        matrix1 = load_matrix_from_user("first")
        matrix2 = load_matrix_from_user("second")

        operation_choice = input("Choose an operation (1, 2, or 3): ")
        operation = matrix_operations.get(operation_choice)

        if not operation:
            raise ValueError("Invalid operation choice.")

        result_matrix = getattr(matrix1, operation["method"])(matrix2)
        print(f"Output of {operation['name']}...\n")

        output_file_path = input("Enter the file path to save the result: ")
        result_matrix.save_to_file(output_file_path)
        print(f"Output file saved to {output_file_path}.")

    except Exception as error:
        print("Error:", error)

def load_matrix_from_user(matrix_number):
    """
    Loads a CompressedMatrix from user input.

    :param matrix_number: Indicates which matrix to load (first or second).
    :return: An instance of CompressedMatrix.
    """
    matrix_path = input(f"Enter the file path for the {matrix_number} matrix: ")
    matrix = CompressedMatrix.load_from_file(matrix_path)
    print(f"{matrix_number.capitalize()} matrix loaded successfully.\n")
    return matrix

# Run the matrix operation function
execute_calculations()
