import cv2

print("📷 Testing Camera Connection...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ 0 වෙනි කැමරාව වැඩ නැත. 1 වෙනි කැමරාව පරීක්ෂා කරයි...")
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if cap.isOpened():
    succ, img = cap.read()
    if succ:
        print("✅ CAMERA WORKING SUCCESSFULLY!")
        cv2.imshow("Lab Test Camera", img)
        cv2.waitKey(0)
    else:
        print("❌ කැමරාව විවෘත වුවත් පින්තූරයක් කියවිය නොහැක (Permission Blocked).")
    cap.release()
else:
    print("❌ වින්ඩෝස් පද්ධතිය විසින් කැමරා උපකරණය සම්පූර්ණයෙන්ම අවහිර කර ඇත!")

cv2.destroyAllWindows()