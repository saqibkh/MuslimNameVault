import os

INPUT_FOLDER = 'names_data'
OUTPUT_FOLDER = 'docs'
SITE_URL = "https://muslimnamevault.com"

# Ensure output directory exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Lists of names for Special Collections

PROPHET_NAMES = [
    "Adam", "Idris", "Nuh", "Hud", "Saleh", "Ibrahim", "Lut", "Ismail", 
    "Ishaq", "Yaqub", "Yusuf", "Ayyub", "Shuaib", "Musa", "Harun", 
    "Daud", "Sulaiman", "Ilyas", "Alyasa", "Yunus", "Zakariya", "Yahya", 
    "Isa", "Muhammad", "Ezra", "Dhul-Kifl", "Uzair", "Luqman"
]

SAHABA_NAMES = [
    # Famous Men
    "Abu Bakr", "Umar", "Uthman", "Ali", "Talha", "Zubair", "Abdur Rahman", 
    "Saad", "Saeed", "Abu Ubaidah", "Bilal", "Anas", "Jabir", "Khalid", 
    "Hamza", "Abbas", "Hassan", "Hussain", "Muawiyah", "Amr", "Zaid", 
    "Usama", "Salman", "Suhail", "Musab", "Yasir", "Ammar",
    # Famous Women
    "Khadija", "Aisha", "Fatima", "Hafsa", "Asma", "Sumayyah", "Nusaybah",
    "Umm Salama", "Zainab", "Ruqayya", "Umm Kulthum", "Mariya", "Juwayriya",
    "Safiyya", "Sawda", "Umm Habiba", "Barakah", "Halima", "Hind", "Laila"
]

TRENDING_2026 = [
    # Boys
    "Ayaan", "Zayd", "Rayyan", "Idris", "Eesa", "Zayan", "Arham", "Aahil", 
    "Ameer", "Danish", "Ehan", "Fahad", "Faiz", "Haider", "Hamdan", "Junaid", 
    "Kayan", "Maaz", "Mikail", "Nael", "Rehan", "Ruhan", "Sahil", "Sarim", 
    "Shayaan", "Shazil", "Taimur", "Uzair", "Umair", "Yazan", "Zavian", 
    "Zayyan", "Zameer", "Farhan", "Saif", "Shahab", "Mirza",
    # Girls
    "Aaliyah", "Maryam", "Inaya", "Safa", "Zoya", "Aleena", "Areesha", "Amani", 
    "Anaya", "Dua", "Daniya", "Eira", "Eliza", "Eshal", "Faria", "Haniya", 
    "Hiba", "Iqra", "Jannat", "Laiba", "Maha", "Mahnoor", "Mina", "Mirha",
    "Mishal", "Muskan", "Noyal", "Pari", "Ramine", "Rida", "Rimsha", 
    "Sana", "Sarah", "Yumna", "Zara", "Zimal"
]

QURANIC_DIRECT = [
    "Muhammad", "Ahmad", "Ibrahim", "Musa", "Isa", "Yusuf", "Maryam", 
    "Yaha", "Zakariya", "Adam", "Nuh", "Ilyas", "Idris", "Hud", "Saleh",
    "Shuaib", "Daud", "Sulaiman", "Ayyub", "Yunus", "Harun", "Luqman",
    "Zaid", "Jibril", "Mikail", "Malik", "Ridhwan", "Aziz", "Hadi", "Nur"
]
