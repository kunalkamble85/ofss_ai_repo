import oracledb

# Set the location of the Oracle Wallet
wallet_location = "C:/kunal/work/OCI/US-region/Wallet_FINERGYAI"  # e.g., "/Users/arya/oracle_wallet"

# Connect to the Oracle database
connection = oracledb.connect(
    user="FINERGYAI_CC_USER",
    password = "EMsingle@12345",
    dsn="finergyai_high", 
    config_dir=wallet_location,
    wallet_location=wallet_location,
    wallet_password="EMsingle@12345"  # If your wallet is password protected, set it here
)

# Create a cursor and execute a test query
cursor = connection.cursor()
cursor.execute("SELECT * FROM WKSP_FINERYAI07CODECONVERSION.EMP")
for row in cursor:
    print(row)

# Close connection
cursor.close()
connection.close()
