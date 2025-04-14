import crypto_func
import shutil
import time
import gui
import os


cwd = crypto_func.cwd
output_folder = crypto_func.output_folder
backup_save = crypto_func.backup_save

def main():
    try:
        if crypto_func.psp_decryption() and crypto_func.quickbms_decrypt():
            print("\nWaiting for file editing")
            gui.main()
            while not os.path.exists(os.path.join(cwd, "modifications_done.flag")): # Check notification flag
                time.sleep(1)
            print("\nDone! Starting encrypting")
            if crypto_func.quickbms_encrypt() and crypto_func.psp_encryption():
                shutil.rmtree(output_folder)
                os.remove(backup_save)
                os.remove(os.path.join(cwd, "modifications_done.flag"))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()