str = "g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj."
num = [ord(c) for c in str]
num1=[]
for i in num:
    if i > 96 and i < 121:
        num1.append(i+2)
    elif i > 120 and i < 123:
        num1.append(i-24)
    else:
        num1.append(i)
print(''.join([chr(c) for c in num1]))
