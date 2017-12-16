Dependencies
-------------
	- The code is implemented in python 2.7. It may not work on different versions of python
 	- The code is implemented and tested on a linux machine
 	- Required libraries are listed in the requirements.txt file.
 	- On a linux machine, you can install them using pip install -r requirements.txt

 Running the code
 ----------------
 	- To run the code, you need to have, in the same directory of the code, two directories named "Home" and "Client" each contains sub-directories, one for each user (e.g., "Rania" and "Ahmed" ...)
 		** If the directory "Client/[user name]" does not exist and the user needs to download a file, the "client.py" program creates the needed directory "Client/[user name]"
 	- You need to run the server first using "python server.py [server port number]"
 	- Then, run the client "python client.py [server name] [server port number]"
 		* In case the server is on the same machien as the client use "localhost" as the [server name]
 		* You need to use the same server port number as the server and client commands
 	- The user will be prompted to enter the user name and password
 	- After authentication, user can execute one of the following commands:
 		* PORT [client port number]
 		* RETR [file name on server]
 			-- File will be saved in Client/[user name]/[file name on server]
 		* STOR [file name on client]
 			-- The file to upload is assumed to be in the current directory (in the same directory as the code)
 			-- File will be saved in Home/[user name]/[file name on client]
 		* LIST
 			-- Will list the files and folders found Home/[user name] and will print them. Note that this is not a recursive list, which means it will only list folders and files and not the contents of subfolders
