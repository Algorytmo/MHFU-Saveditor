import subprocess
import shutil
import os


# File constant
FILESIZE_EXPECTED = 0x16A100  # 1483008 bytes expected
FILESIZE_PSP_ENCRYPTED = 0x16A110

# Paths
cwd = os.getcwd()
quickbms_dir = os.path.join(cwd, "scripts/")
quickbms = os.path.join(quickbms_dir, "quickbms.exe")
quickbms_decr = os.path.join(quickbms_dir, "MHFU_SaveDecrypter.bms")
quickbms_encr = os.path.join(quickbms_dir, "MHFU_SaveEncrypter.bms")
sed_pc_exe = os.path.join(cwd, "SED-PC/SED-PC.exe")
decr_dict =  os.path.join(cwd, "data/MHFUdic_de.bin")
encr_dict =  os.path.join(cwd, "data/MHFUdic_en.bin")
output_folder = os.path.join(cwd, "savedata/")
os.makedirs(output_folder, exist_ok=True)
shutil.copy(decr_dict, output_folder)
shutil.copy(encr_dict, output_folder)

def find_region():
    # Find game region with folder name
    game_region = {
        "ULES01213": "MHP2G_EU",
        "ULUS10391": "MHP2G_US",
        "ULJM05500": "MHP2G_JP"
    }
    for folder_name, region in game_region.items():
        if os.path.exists(os.path.join(cwd, f"{folder_name}")):
            directory = os.path.join(cwd, f"{folder_name}/")
            return region, directory

region, directory = find_region()

def region_key():
    # Find game region key
    if region == "MHP2G_EU":
        #SHA1SALT = "3Nc94Hq1zOLh8d62Sb69"  # EU salt
        ST_key =  os.path.join(cwd, "data/MHFU_key.bin")
        print("Selected: Europe (MHP2G_EU)")
        return ST_key
    elif region == "MHP2G_US":
        #SHA1SALT = "3Nc94Hq1zOLh8d62Sb69"  # US uses the same salt as EU
        ST_key =  os.path.join(cwd, "data/MHFU_key.bin")
        print("Selected: USA (MHP2G_US)")
        return ST_key
    elif region == "MHP2G_JP":
        #SHA1SALT = "S)R?Bf8xW3#5h9lGU8wR"  # JP salt
        ST_key =  os.path.join(cwd, "data/MHP2g_key.bin")
        print("Selected: Japan (MHP2G_JP)")
        return ST_key
    else:
        print("Invalid region! Exiting...")
        return False

ST_key = region_key()
save_file = os.path.join(cwd, f"{directory}/MHP2NDG.BIN")
backup_save = os.path.join(cwd, os.path.basename(f"{save_file}.bak"))
shutil.copy(save_file, backup_save)

def psp_decryption():
    print("\n--- PSP Decryption ---")
    # Check file size
    save_size = os.path.getsize(save_file)
    if save_size == FILESIZE_EXPECTED:
        print("The save file seems to be PSP decrypted already.")
        return True
    elif save_size == FILESIZE_PSP_ENCRYPTED:
        print("The save file seems to still be PSP encrypted. Starting decryption...")
        # Start SED-PC.exe for PSP decryption
        subprocess.run([sed_pc_exe, "-d", save_file, save_file, ST_key])
        # Check file size after decryption
        save_size = os.path.getsize(save_file)
        if save_size == FILESIZE_EXPECTED:
            print("PSP Decryption successful!")
            return True
        else:
            print("PSP Decryption might have failed.")
            return False
    else:
        print("Unknown save file size. Cannot proceed.")
        return False

def quickbms_decrypt():
    subprocess.run([quickbms, "-a", region, "-Y", quickbms_decr, save_file, output_folder])
    return True

def quickbms_encrypt():
    subprocess.run([quickbms, "-a", region, "-a", "list", "-a", "no", quickbms_encr, save_file, output_folder])
    os.remove(save_file)
    newfile = os.path.join(output_folder, "MHP2NDG.BIN")
    shutil.copy(newfile, directory)
    return True

def psp_encryption():
    # Start SED-PC.exe for PSP encryption
    param_file = os.path.join(cwd, f"{directory}/PARAM.SFO")
    print("\n--- PSP Encryption ---")
    # Check file size
    save_size = os.path.getsize(save_file)
    if save_size == FILESIZE_EXPECTED:
        print("The save file seems to be PSP decrypted. Starting encryption...")
        ret = subprocess.run([sed_pc_exe, "-e", save_file, param_file, save_file, ST_key])
        # Check file size after encryption
        save_size = os.path.getsize(save_file)
        if ret.returncode == 0 and save_size == FILESIZE_PSP_ENCRYPTED:
            print("PSP Encryption successful!")
            return True
        else:
            raise RuntimeError("PSP Encryption might have failed.")
    elif save_size == FILESIZE_PSP_ENCRYPTED:
        print("The save file seems to be PSP encrypted already.")
        return True
    else:
        print("Unknown save file size. Cannot proceed.")
        return False
