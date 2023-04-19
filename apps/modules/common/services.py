import secrets, string


class CommonServices:
    def generate_unique_string(length):
        """
        function to generate the access_key and password for Application
        """
        res = "".join(
            secrets.choice(string.ascii_letters + string.digits) for i in range(length)
        )
        return str(res)
