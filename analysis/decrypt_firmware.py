#!/usr/bin/env python3
"""
Decrypt FirmwareUpdate.qz using the reversed X2Crypt algorithm.

From Quadzilla.dll decompilation:
  EncryptHexFile: encrypted = plaintext ^ passwordKey[i%8] ^ prev; prev = encrypted
  DecryptHexFile: plaintext = encrypted ^ passwordKey[i%8] ^ prev; prev = encrypted

The .pwk file contains the passwordKey directly (8 bytes).
The .pwd file contains the password (8 bytes), used to regenerate passwordKey via GeneratePasswordKey().
"""
import os
import hashlib

BASE = r'extracted/from_exe/ckz_75O0/FirmwareUpdate'

# Substitution table from X2Crypt constructor (e_table)
E_TABLE = [
    3328402341, 4168907908, 4000806809, 4135287693, 4294111757, 3597364157,
    3731845041, 2445657428, 1613770832, 33620227, 3462883241, 1445669757,
    3892248089, 3050821474, 1303096294, 3967186586, 2412431941, 528646813,
    2311702848, 4202528135, 4026202645, 2992200171, 2387036105, 4226871307,
    1101901292, 3017069671, 1604494077, 1169141738, 597466303, 1403299063,
    3832705686, 2613100635, 1974974402, 3791519004, 1033081774, 1277568618,
    1815492186, 2118074177, 4126668546, 2211236943, 1748251740, 1369810420,
    3521504564, 4193382664, 3799085459, 2883115123, 1647391059, 706024767,
    134480908, 2512897874, 1176707941, 2646852446, 806885416, 932615841,
    168101135, 798661301, 235341577, 605164086, 461406363, 3756188221,
    3454790438, 1311188841, 2142417613, 3933566367, 302582043, 495158174,
    1479289972, 874125870, 907746093, 3698224818, 3025820398, 1537253627,
    2756858614, 1983593293, 3084310113, 2108928974, 1378429307, 3722699582,
    1580150641, 327451799, 2790478837, 3117535592, 0, 3253595436,
    1075847264, 3825007647, 2041688520, 3059440621, 3563743934, 2378943302,
    1740553945, 1916352843, 2487896798, 2555137236, 2958579944, 2244988746,
    3151024235, 3320835882, 1336584933, 3992714006, 2252555205, 2588757463,
    1714631509, 293963156, 2319795663, 3925473552, 67240454, 4269768577,
    2689618160, 2017213508, 631218106, 1269344483, 2723238387, 1571005438,
    2151694528, 93294474, 1066570413, 563977660, 1882732616, 4059428100,
    1673313503, 2008463041, 2950355573, 1109467491, 537923632, 3858759450,
    4260623118, 3218264685, 2177748300, 403442708, 638784309, 3287084079,
    3193921505, 899127202, 2286175436, 773265209, 2479146071, 1437050866,
    4236148354, 2050833735, 3362022572, 3126681063, 840505643, 3866325909,
    3227541664, 427917720, 2655997905, 2749160575, 1143087718, 1412049534,
    999329963, 193497219, 2353415882, 3354324521, 1807268051, 672404540,
    2816401017, 3160301282, 369822493, 2916866934, 3688947771, 1681011286,
    1949973070, 336202270, 2454276571, 201721354, 1210328172, 3093060836,
    2680341085, 3184776046, 1135389935, 3294782118, 965841320, 831886756,
    3554993207, 4068047243, 3588745010, 2345191491, 1849112409, 3664604599,
    26054028, 2983581028, 2622377682, 1235855840, 3630984372, 2891339514,
    4092916743, 3488279077, 3395642799, 4101667470, 1202630377, 268961816,
    1874508501, 4034427016, 1243948399, 1546530418, 941366308, 1470539505,
    1941222599, 2546386513, 3421038627, 2715671932, 3899946140, 1042226977,
    2521517021, 1639824860, 227249030, 260737669, 3765465232, 2084453954,
    1907733956, 3429263018, 2420656344, 100860677, 4160157185, 470683154,
    3261161891, 1781871967, 2924959737, 1773779408, 394692241, 2579611992,
    974986535, 664706745, 3655459128, 3958962195, 731420851, 571543859,
    3530123707, 2849626480, 126783113, 865375399, 765172662, 1008606754,
    361203602, 3387549984, 2278477385, 2857719295, 1344809080, 2782912378,
    59542671, 1503764984, 160008576, 437062935, 1707065306, 3622233649,
    2218934982, 3496503480, 2185314755, 697932208, 1512910199, 504303377,
    2075177163, 2824099068, 1841019862, 739644986
]


def generate_password_key(password_2x4):
    """
    Generate passwordKey from password using the e_table.
    Password is a 2x4 byte array (flattened to 8 bytes).
    """
    password = [[0]*4, [0]*4]
    for i in range(2):
        for j in range(4):
            password[i][j] = password_2x4[i*4 + j]
    
    array = [0, 0]  # uint[2]
    for col in range(4):
        for row in range(2):
            if col == 0:
                array[row] = E_TABLE[password[row][col]]
            else:
                val = E_TABLE[password[row][col]]
                shift = (col % 4) * 8
                left = (val << shift) & 0xFFFFFFFF
                right = (val >> (32 - shift)) & 0xFFFFFFFF
                rotated = (left + right) & 0xFFFFFFFF
                array[row] ^= rotated
    
    pk = bytearray(8)
    for col in range(4):
        for row in range(2):
            v = array[row]
            for _ in range(col):
                v //= 256
            pk[row * 4 + col] = v & 0xFF
    
    return bytes(pk)


def decrypt_qz(qz_data, password_key):
    """
    Decrypt .qz file using the X2Crypt cipher-chain.
    DecryptHexFile:
        prev = 0
        for each byte:
            encrypted = qz_byte
            plaintext = encrypted ^ passwordKey[i%8] ^ prev
            prev = encrypted
    """
    result = bytearray(len(qz_data))
    prev = 0
    for i, b in enumerate(qz_data):
        plaintext = b ^ password_key[i % 8] ^ prev
        prev = b  # Note: prev = encrypted byte (the input), NOT the plaintext
        result[i] = plaintext
    return bytes(result)


def main():
    # Read keys
    with open(os.path.join(BASE, 'FirmwareUpdate.pwd'), 'rb') as f:
        pwd_data = f.read()
    with open(os.path.join(BASE, 'FirmwareUpdate.pwk'), 'rb') as f:
        pwk_data = f.read()
    
    print(f"Password (.pwd): {pwd_data.hex()}")
    print(f"PasswordKey (.pwk): {pwk_data.hex()}")
    
    # Method 1: Use .pwk directly as passwordKey
    print("\n=== Method 1: Using .pwk as passwordKey directly ===")
    with open(os.path.join(BASE, 'FirmwareUpdate.qz'), 'rb') as f:
        qz_data = f.read()
    
    decrypted = decrypt_qz(qz_data, pwk_data)
    
    # Check if it looks like Intel HEX
    print(f"First 64 bytes: {decrypted[:64].hex()}")
    first_text = decrypted[:64].decode('ascii', errors='replace')
    print(f"As text: {first_text}")
    
    if decrypted[0:1] == b':':
        print("SUCCESS! Decrypted to Intel HEX format!")
    elif all(32 <= b < 127 or b in (0x0D, 0x0A) for b in decrypted[:100]):
        print("Looks like text content!")
    
    # Save
    out_path = os.path.join(BASE, 'FirmwareUpdate_decrypted.hex')
    with open(out_path, 'wb') as f:
        f.write(decrypted)
    print(f"Saved to: {out_path}")
    print(f"Decrypted size: {len(decrypted)} bytes")
    
    # Method 2: Generate passwordKey from password via e_table
    print("\n=== Method 2: Generating passwordKey from .pwd via e_table ===")
    generated_key = generate_password_key(pwd_data)
    print(f"Generated key: {generated_key.hex()}")
    print(f"Matches .pwk:  {generated_key == pwk_data}")
    
    decrypted2 = decrypt_qz(qz_data, generated_key)
    print(f"First 64 bytes: {decrypted2[:64].hex()}")
    first_text2 = decrypted2[:64].decode('ascii', errors='replace')
    print(f"As text: {first_text2}")
    
    if decrypted2[0:1] == b':':
        print("SUCCESS! Decrypted to Intel HEX format!")
        out_path2 = os.path.join(BASE, 'FirmwareUpdate_decrypted_v2.hex')
        with open(out_path2, 'wb') as f:
            f.write(decrypted2)
        print(f"Saved to: {out_path2}")
    
    # Show first few lines if text
    for name, data in [("Method 1", decrypted), ("Method 2", decrypted2)]:
        is_text = all(32 <= b < 127 or b in (0x0D, 0x0A) for b in data[:200])
        if is_text:
            print(f"\n=== {name} first lines ===")
            lines = data.decode('ascii', errors='replace').split('\n')
            for line in lines[:20]:
                print(f"  {line.rstrip()}")
    
    print("\nDone!")


if __name__ == '__main__':
    main()
