PC Port of save data encrypter / decrypter.
Notes for this version: It’s fairly simple to use this tool.

Usage:

  sed -e [Input File] [PARAM.SFO] [Output File] [Game Key File]

  sed -d [Input File] [Output File] [Game Key File]

Where:

  ‘-e’ tells it to encrypt, ‘-d’ to decrypt.

  [Input File] is the file to encrypt or decrypt

  [Output File] is the name of the file to save to

  [PARAM.SFO] is the location of the PARAM.SFO file whose hashes should be updated

  [Game Key File] is the full path to the file which has the game key


The (extremely) untidy source code can be found at GitHub (https://github.com/hgoel0974/SED-PC)

Credits go to the team behind libkirk and to the PPSSPP team for the sceChnnlsv implementation, these two libraries made my work easy.
