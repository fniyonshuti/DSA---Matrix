import os
import re  # Ensure the re module is imported

class CompressedMatrix:
    """
    Represents a compressed matrix.
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
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()

            if len(lines) < 2:
                raise ValueError(
                    f"File {file_path} does not contain enough lines for matrix dimensions."
                )

            # Parse dimensions
            row_pattern = re.match(r'rows=(\d+)', lines[0].strip())  # Use re.match() for row
            col_pattern = re.match(r'cols=(\d+)', lines[1].strip())  # Use re.match() for column

            if not row_pattern or not col_pattern:
                raise ValueError(
                    f"Invalid dimension format in file {file_path}. Expected 'rows=X' and 'cols=Y'."
                )

            total_rows = int(row_pattern[1])
            total_cols = int(col_pattern[1])

            matrix_instance = cls(total_rows, total_cols)

            # Parse non-zero elements
            for i in range(2, len(lines)):
                line = lines[i].strip()
                if line == "":
                    continue  # Skip empty lines

                match = re.match(r'\((\d+),\s*(\d+),\s*(-?\d+)\)', line)
                if not match:
                    raise ValueError(
                        f"Invalid format at line {i + 1} in file {file_path}: {line}."
                    )

                row_index = int(match[1])
                col_index = int(match[2])
                value = int(match[3])

                matrix_instance.set_value(row_index, col_index, value)

            return matrix_instance
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}.")
        except Exception as e:
            raise e

    def get_value(self, row_index, col_index):
        """
        Retrieves the value of an element at a specific row and column.

        :param row_index: The row index of the element.
        :param col_index: The column index of the element.
        :return: The value at the specified position, or 0 if not set.
        """
        key = (row_index, col_index)
        return self.non_zero_elements.get(key, 0)  # Return the value or 0 if not found

    def set_value(self, row_index, col_index, value):
        """
        Sets the value of an element at a specific row and column.

        :param row_index: The row index where the value should be set.
        :param col_index: The column index where the value should be set.
        :param value: The value to set at the specified position.
        """
        if row_index >= self.row_count:
            self.row_count = row_index + 1  # Update row count if needed
        if col_index >= self.column_count:
            self.column_count = col_index + 1  # Update column count if needed

        key = (row_index, col_index)
        self.non_zero_elements[key] = value  # Set the value in the dictionary

    def add(self, other_matrix):
        """
        Adds two compressed matrices.

        :param other_matrix: The other CompressedMatrix to add.
        :return: A new CompressedMatrix that is the sum of the two matrices.
        """
        if self.row_count != other_matrix.row_count or self.column_count != other_matrix.column_count:
            raise ValueError("Matrices must have the same dimensions for addition.")

        result_matrix = CompressedMatrix(self.row_count, self.column_count)

        # Add elements from the first matrix
        for (row_index, col_index), value in self.non_zero_elements.items():
            result_matrix.set_value(row_index, col_index, value)

        # Add elements from the second matrix
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
        if self.row_count != other_matrix.row_count or self.column_count != other_matrix.column_count:
            raise ValueError("Matrices must have the same dimensions for subtraction.")

        result_matrix = CompressedMatrix(self.row_count, self.column_count)

        # Subtract elements from the second matrix from the first matrix
        for (row_index, col_index), value in self.non_zero_elements.items():
            result_matrix.set_value(row_index, col_index, value)

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

    def __str__(self):
        """
        Converts the CompressedMatrix to a string representation.

        :return: The string representation of the CompressedMatrix.
        """
        result = f"rows={self.row_count}\ncols={self.column_count}\n"
        for key, value in self.non_zero_elements.items():
            result += f"({key[0]}, {key[1]}, {value})\n"
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
        # Define available operations
        matrix_operations = {
            '1': {"name": "multiplication", "method": "multipy"},
            '2': {"name": "subtraction", "method": "subtract"},
            '3': {"name": "addition", "method": "add"},
        }

        # Display the operations menu
        print("choose  operations:")
        for key, operation in matrix_operations.items():
            print(f"{key}: {operation['name']}")

        first_matrix_path = input("Enter the file path for the first matrix: ")
        matrix1 = CompressedMatrix.load_from_file(first_matrix_path)
        print("First matrix loading...\n")

        second_matrix_path = input("Enter the file path for the second matrix: ")
        matrix2 = CompressedMatrix.load_from_file(second_matrix_path)
        print("Second matrix loading...\n")

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

# Run the matrix operation function
execute_calculations()
