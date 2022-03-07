def distance_hamming(str1, str2):
    if len(str1) > len(str2):
        str2 = str2 + (len(str1)-len(str2))*' '
    elif len(str2) > len(str1):
        str1 = str1 + (len(str2)-len(str1))* ' '
    return sum(1 for (a, b) in zip(str1, str2) if a != b)