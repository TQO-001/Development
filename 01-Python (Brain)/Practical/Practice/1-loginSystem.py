def dash(num = 8, char = "="):
    print(char*4*num);

def greet(name = "User"):
    print("Welcome back,", name)

user1 = {
    "username": "Joe",
    "password": 1234
}

print("Please enter Login details:")

notLogin = True
while(notLogin):
    checkUsername = input("\tusername: ")
    if (checkUsername.lower() == user1["username"].lower()):
        checkPassword = int(input("\tpassword: "))
        if (checkPassword == user1["password"]):
            notLogin = False
        else:
            print("Incorrect Password!")
    else:
        print("Incorrect Username!")

    if (notLogin == False):
        print("Login Successful!")
    else:
        print("Login Failed! Please try again.")
    dash(8, "-")
