"""
Entertainment features
"""
import random


def tell_joke():
    """Tell a joke"""
    jokes = [
        "Neden bilgisayarlar soğuk? Çünkü Windows'ları açık bırakıyorlar!",
        "Bir programcı markete gider. Eşi der ki: 'Süt al, eğer yumurta varsa 6 tane al.' Programcı 6 süt alır.",
        "Neden Python programcıları karanlıkta çalışır? Çünkü onlar Python!",
        "Bir yazılımcı ne zaman mutlu olur? Debug yaparken!",
        "JARVIS'e sormuşlar: 'En sevdiğin şey nedir?' JARVIS: 'Iron Man tabii ki!'",
    ]
    joke = random.choice(jokes)
    return True, joke


def flip_coin():
    """Flip a coin"""
    result = random.choice(["Yazı", "Tura"])
    return True, f"Yazı tura atıldı: {result}"


def random_number(min_num=1, max_num=100):
    """Generate random number"""
    num = random.randint(min_num, max_num)
    return True, f"Rastgele sayı ({min_num}-{max_num}): {num}"


def tell_story():
    """Tell a short story"""
    stories = [
        "Bir zamanlar uzak bir galakside, bir yapay zeka asistanı vardı. Adı JARVIS'ti ve sahibine her konuda yardım ediyordu. Bir gün sahibi 'Bilgisayarı kapat' dedi. JARVIS düşündü: 'Ama ben bilgisayarın içindeyim!' Sonra güldü ve bilgisayarı kapatmadı. Akıllı asistan!",
        "Bir programcı vardı, her gün kod yazardı. Bir gün bir bug buldu, düzeltti. Ertesi gün başka bir bug buldu, onu da düzeltti. Bu böyle devam etti. Sonunda programcı anladı: Bug'lar bitmez, sadece değişir!",
    ]
    story = random.choice(stories)
    return True, story

