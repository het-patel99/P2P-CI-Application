# P2P-CI-Application

This is a Peer-to-Peer application where all the peers have their own rfc files. They will be connected to the server and will share the rfc numbers of the files that they have with them. New clients who wants a particular rfc they can request server to give them a list of client peers who already have that particular rfc and client will directly connect to that client and will get that rfc file.

## Steps to run

### Method - 1 ()
1. Download .zip file of this project and extract. OR Git clone "https://github.com/het-patel99/P2P-CI-Application.git".
2. Create a copy of extracted file in different directory OR clone again into different directory.
3. Separate some rfc files from the rfcs folder, select any 2-3 files and paste that into rfcs folder of the copy project. (Ex. there are total 1,2,3,4,5,6 rfc files originally. We have downloaded zip in 2 different directory, hence 1st directories rfcs folder will contain 1,2,3,4 rfc files and 2nd directories folder will have 5,6 rfc file. Remove accordingly.
4. Start the server by running "python3 server.py" from the src directory.
5. Start the client by running "python3 client.py" from the src directory. (Client-1)
6. Go to copy of this project and from the src directory run "python3 client.py" (Client-2)   
7. Now you can test all the funcitonalities ADD, LOOKUP, LIST ALL.
8. After requesting rfc from peers, the requested rfc file will be downloaded in rfcs directory of requested client's

## Additional Instructions 

Here we will be testing on the local, so for the demo server is on port 7735, first client is by default on 8080. Now if you want another client create a copy of this whole application/project and paste it in some other directory. Now open "client.py" and change the port number to any other port number. Run "client.py" and you will have your new client running. (This is done because we are want to show demo on same mahine, i.e. 1 server and 2 clients on same machine). Now you have both the clients connected, add their own rfcs and make sure that each client have thhat rfc number file in the rfcs directory which is just one step above client.py file. Atleast add one rfc in both the clients(Lets say rfc1 in client 1, rfc2 in client2). Lookup for rfc2 from client1 or vice versa and then request for rfc1 from client2 or rfc2 from client1. At last that rfc file will be downloaded into the rfcs folder/directory you created for that particular client.