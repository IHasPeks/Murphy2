import random
from config import TWITCH_PREFIX

# variables used for commands below
cannon_count = 0


async def handle_command(bot, message):
    global cannon_count
    command = message.content[len(TWITCH_PREFIX) :].split(" ")[0]

    if command == "help":
        await message.channel.send(
            "Available commands: https://raw.githubusercontent.com/IHasPeks/Murphy2/main/commands.md. if the command you are looking for isnt listed. it may be unavailable at this time",
        )
    elif command == "test":
        await message.channel.send(
            "test",
        )
    elif command == "ping":
        await message.channel.send(
            "Pong!",
        )
    elif command == "bald":
        await message.channel.send(
            "Looks like Peks forgot his wig today!",
        )
    elif command == "int":
        await message.channel.send(
            "Peks is practicing his diving skills in-game, don't mind the score. KEKW",
        )
    elif command == "tea":
        await message.channel.send(
            "Peks prefers his tea like his gameplay, dark and intense. PauseChamp",
        )
    elif command == "bestbot":
        await message.channel.send(
            "I'm flattered, but we all know Peks is the real MVP here. NOT... I AM THE BEST BOT elmoFire ",
        )
    elif command == "garen":
        await message.channel.send(
            "DEMACIA! garen gaming Garen Peks loves spinning to win. garenPog",
        )
    elif command == "jam":
        await message.channel.send(
            "blobSlide blobSlide blobSlide ratJAM blobDance ratJAM GroupJAM blobDance catJAM pepeJam pepeJAMJAMJAM pepeJAMJAMJAM pepeJam AMOGUS AMOGUS AMOGUS dogePLS dogePLS dogePLS dogePLS dogePLS dogJAM dogJAM GroupJAM BANGER BANGER BANGER GroupJAM GroupJAM ",
        )
    elif command == "pog":
        await message.channel.send("Pog? Peks is the definition of Pog. PogChamp")
    elif command == "masters":
        await message.channel.send(
            "Masters? Easy. Peks is on his way, just a few... hundred games more.",
        )
    elif command == "milkpasta":
        await message.channel.send("Peks's secret recipe. Don't knock it till you try it!")
    elif command == "bye":
        await message.channel.send(
            f"{message.author.mention} is leaving, Peks will probably miss you.",
        )
    elif command == "smelly":
        await message.channel.send(
            "Whoa, whoa. Peks took a shower... last week. Do rats even take showers!",
        )
    elif command == "robinvroom":
        await message.channel.send(
            "https://clips.twitch.tv/AltruisticEnergeticMochaPicoMause-VJCUTug58An6d2JM ",
        )
    elif command == "slingshot":
        await message.channel.send(
            "https://clips.twitch.tv/DignifiedHelpfulTruffleYouDontSay-mCxDlAu3CJdz87pr",
        )
    elif command == "iloveu":
        await message.channel.send(
            "https://clips.twitch.tv/CleverPowerfulAnacondaShazBotstix-obqsk2mZb_CN_G2i",
        )
    elif command == "brb":
        await message.channel.send(
            f"{message.author.mention} will be right back, probably grabbing more snacks.",
        )
    elif command == "4":
        await message.channel.send(
            "A GIGACHAD 5Head big brain person who helps me find bugs, AND who also edits emotes",
        )
    elif command == "laws":
        await message.channel.send("1. Eat Pizza 2. Spell it alwase 3. Don't play runescape")
    elif command == "returned":
        await message.channel.send(f"{message.author.mention} is back, yippee peepoArrive")
    elif command == "flauenn":
        await message.channel.send(
            "Chatting",
        )
    elif command == "song":
        await message.channel.send(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
    elif command == "raidmsg":
        await message.channel.send(
            "ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce",
        )
    elif command == "mad":
        await message.channel.send(
            "TrollFace mad? Never. Peks is the epitome of calm and collected. *Table flip*",
        )
    elif command == "4song":
        await message.channel.send(
            "https://www.youtube.com/watch?v=u8ccGjar4Es",
        )
    elif command == "roan":
        await message.channel.send(
            "Woan is vewy UwU Gayge PogPlanting",
        )
    elif command == "Roan":
        await message.channel.send(
            "you have found Roan's secret command. Roan is amazing peepoLove UwU",
        )
    elif command == "schedule":
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/949012582595964958/1155562279367098508/chedule_1.png?ex=65db7e3c&is=65c9093c&hm=d81efc1bfa547d89165a731363578564684ab1aad849a01d6cc3b8eb118cb224&",
        )
    elif command == "scream":
        await message.channel.send(
            "AHHHH! Just kidding, Peks is too cool to scream. Or is he just a little girl?",
        )
    elif command == "blob":
        await message.channel.send(
            "Blobbing around with Peks. It's more fun than it sounds. blobSlide blobSlide blobSlide ratJAM blobDance ratJAM GroupJAM blobDance catJAM pepeJam pepeJAMJAMJAM pepeJAMJAMJAM pepeJam AMOGUS AMOGUS AMOGUS dogePLS dogePLS dogePLS dogePLS dogePLS dogJAM dogJAM GroupJAM BANGER BANGER BANGER GroupJAM GroupJAM",
        )
    elif command == "1":
        await message.channel.send("Number one in our hearts and occasionally in the game.")
    elif command == "XD":
        await message.channel.send(
            "XD indeed. TrollFace mad?XD",
        )
    elif command == "shane":
        await message.channel.send(
            "shane found a bug in discord POGGERS",
        )
    elif command == "birthday":
        await message.channel.send(
            "https://www.youtube.com/watch?v=wC4y4b8iyR0",
        )
    elif command == "ratbucket":
        await message.channel.send(
            "One day peks will get into the ratbucket Ratge ihaspeDerp",
        )
    elif command == "caedrel":
        await message.channel.send(
            "https://clips.twitch.tv/GentleNimbleStarPrimeMe-sZRWuCU6llKgbAlh",
        )
    elif command == "info":
        await message.channel.send(
            "Looking for info? Peks's life is an open book. Mostly. Just ask him any question and he will be sure to not answer",
        )
    elif command == "pi":
        await message.channel.send(
            "3.14159... Peks's favorite number because it's the number of seconds he's spent on a grey screen on league.",
        )
    elif command == "works":
        await message.channel.send(
            "It works! Just like Peks's charm. 60% of the time, it works every time.",
        )
    elif command == "bestcheese":
        await message.channel.send(
            "The best cheese? Peks's gameplay. Just kidding, it's Feta.",
        )
    elif command == "rgbjam":
        await message.channel.send(
            "RGB Jam, for when you need your music to be as colorful as your lighting. blobDance blobDance blobDance blobDance blobSlide blobSlide blobSlide blobSlide blobSlide peepoDJ blobDance peepoDJ blobDance peepoDJ blobDance peepoDJ raveDumper peepoDJ raveDumper peepoDJ raveDumper peepoDJ skeletonDance peepoDJ skeletonDance peepoDJ Danceboye Danceboye Danceboye Danceboye peepoDJ peepoDJ peepoDJ peepoDJ peepoDJ peepoDJ peepoDJ ",
        )
    elif command == "8ball":
        await message.channel.send("Magic 8-ball says: Definitely! Peks agrees.")
    elif command == "forgore":
        await message.channel.send(
            "I FORGORR ☠ ☠ ☠ ☠ ☠? Peks never forgets... except when he does.",
        )
    elif command == "quotes":
        await message.channel.send(
            "'If at first you don't succeed, blame the lag.'6Head -Peks ",
        )
    elif command == "elo":
        await message.channel.send(
            "ELO? It's not just a number, it's a state of mind. Peks is currently Dogshit III 75 LP on this account.",
        )
    elif command == "lurk":
        await message.channel.send(
            f"{message.author.mention} is lurking, Peks appreciates your silent support. dogeLurk",
        )
    elif command == "e":
        await message.channel.send(
            "Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE ",
        )
    elif command == "leaf":
        await message.channel.send(
            "Leaf it to Peks to turn over a new leaf every stream. Leaf",
        )
    elif command == "server":
        await message.channel.send("Server? More like serv-her another win, am I right?")
    elif command == "anime":
        await message.channel.send(
            "Muercie is officially an anime enjoyer. time for an anime night with Peks? What are we watching?",
        )
    elif command == "tiktok":
        await message.channel.send(
            "TikTok on the clock, but the party don't stop. https://www.tiktok.com/@ihaspeks .",
        )
    elif command == "cheer":
        await message.channel.send(
            "Give me a P! Give me an E! Give me a K! Give me an S! What does that spell? peepoCheer P peepoCheer E peepoCheer K peepoCheer S peepoCheer",
        )
    elif command == "rugo":
        await message.channel.send("Rugo? Actually i wonder where he went?")
    elif command == "teiva":
        await message.channel.send(
            "Teiva, Gayge the unsung hero of Peks's streams. Always there, always supportive.",
        )
    elif command == "idea":
        await message.channel.send(
            "Got an idea? Peks is all ears. As long as it involves gaming or snacks. dogeHead",
        )
    elif command == "squat":
        await message.channel.send(
            "Squat challenge! Peks is doing one for every sub. Feel the burn! DOGEDANCE S DOGEDANCE Q DOGEDANCE U DOGEDANCE A DOGEDANCE T DOGEDANCE S DOGEDANCE ",
        )
    elif command == "subathon":
        await message.channel.send(
            "Ding SubRATathon on the 1st of july. Multiple activities and events. 1v1 and 2v2 tournament -- JOIN THE DISCORD with the command ?discord -- Other events, such as Bingo, Customs, Spoopy games and much much more. Don't forget to join discord to be updated and learn more --- USE THE COMMAND ?discord Ding",
        )
    elif command == "rugothon":
        await message.channel.send(
            "Ding SubRUGOthon on the 1st of july. Multiple activities and events. 1v1 and 2v2 rugo rumble -- JOIN THE RUGOCORD with the command ?rugocord -- Other events, such as Rugy Bingo, Rugo Customs, Spooky Rugo games and much much more. Don't forget to join rugocord to be updated and learn more --- USE THE COMMAND ?rugocord Ding",
        )
    elif command == "crazy":
        await message.channel.send(
            "Crazy? i was crazy once. i locked myself in a room, a concrete room, a concrete room with chat, my chat is full of rats which make me crazy",
        )
    elif command == "pilk":
        await message.channel.send(
            "Pilk? Peks's favorite drink. It's... unique. i hear Muercie is officially a pilk enjoyer",
        )
    elif command == "video":
        await message.channel.send(
            "New video alert! Peks has uploaded another masterpiece. Go check it out. https://www.youtube.com/watch?v=vE0iNgwDl8E ",
        )
    elif command == "chatplaylist":
        await message.channel.send(
            "https://youtu.be/OryF8smba2A",
        )
    elif command == "flash":
        await message.channel.send(
            "Thats an NA flash there bro KEKW",
        )
    elif command == "cousin":
        await message.channel.send(
            "okayCousin BedgeCousin comfycousin CoolCousin cousin cousins cousint FarAwayCousin HeyCousin MadCousin POGCousin SadCousin StrongCousin WeirdCousin WeirdPizzaCousin zazacousin ratin CuteCousin WeirdCousingers ",
        )
    elif command == "1kfollower":
        await message.channel.send(
            "1k followers! Peks couldn't have done it without you. Here's to 1k more! ItsChrisyBaby was the 1000th follower BASED",
        )
    elif command == "tails":
        await message.channel.send(
            "tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL ",
        )
    elif command == "tanked":
        await message.channel.send(
            "Tanked? Peks prefers the term 'strategically positioned at the bottom of the leaderboard' https://clips.twitch.tv/BusyHorribleWombatBlargNaut-OQYkzliVdYHyFnj4 .",
        )
    elif command == "cousins":
        await message.channel.send(
            "okayCousin BedgeCousin comfycousin CoolCousin cousin cousins cousint FarAwayCousin HeyCousin MadCousin POGCousin SadCousin StrongCousin WeirdCousin WeirdPizzaCousin zazacousin ratin ",
        )
    elif command == "art":
        await message.channel.send(
            "yes peks is actively looking for any kind of commissions please tell him all about it Tomfoolery",
        )
    elif command == "emotes":
        await message.channel.send(
            "Looking for emotes? Here's the link to express your Peks love in chat: 7TV link: https://7tv.app/emote-sets/645c2a418e6b5a947a6131c7 BetterTTV link: https://betterttv.com/users/6024310f0b26f21727617c8f ",
        )
    elif command == "jele":
        await message.channel.send(
            "Jele? A rare delicacy in Peks's stream. Best served with humor and good vibes. https://imgur.com/a/LbpVdxF ",
        )
    elif command == "cs":
        await message.channel.send(
            "CS? In Peks's world, it stands for 'Constantly Smiling' https://imgur.com/a/lWCWvER.",
        )
    elif command == "uwu":
        await message.channel.send(
            "UwU, what's this?!?1 Anyothew adowabwe moment on Peks's stweam.",
        )
    elif command == "nothing":
        await message.channel.send("")
    elif command == "top":
        await message.channel.send(
            "Top? Peks is always on top of his game. Except when he's not.",
        )
    elif command == "t":
        await message.channel.send(
            "T for Tryhard. Peks's middle name when it comes to gaming.",
        )
    elif command == "9ball":
        await message.channel.send(
            "what is 9ball? use ?8ball instead",
        )
    elif command == "subs":
        await message.channel.send("Subs, assemble! Your support makes Peks's day, every day.")
    elif command == "discord":
        await message.channel.send(
            "Join Peks's Discord for more fun and games off-stream. See you there!: REPLACE THIS WITH DISCORD LINK",
        )
    elif command == "vid":
        await message.channel.send(
            "Vid? Peks has plenty. Check out his newest video that is 2 years old.",
        )
    elif command == "scam":
        await message.channel.send(
            "Scam? The only scam here is how addictively fun Peks's streams are. KEKW",
        )
    elif command == "weather":
        await message.channel.send(
            "Weather report: It's always sunny in Peks's stream. Bring sunglasses.",
        )
    elif command == "penta":
        await message.channel.send("Penta kill! Oh wait, that was just Peks dreaming again.")
    elif command == "latege":
        await message.channel.send("ADD LATEGE TIMER HERE")
    elif command == "joke":
        await message.channel.send("we are not bringing this back...")
    elif command == "truth":
        await message.channel.send(
            "The truth? You can't handle the truth! But Peks will tell you anyway.",
        )
    elif command == "spam":
        # Extract the message to spam, removing the command part
        spam_message = message.content[len(TWITCH_PREFIX) + len(command) + 1 :].strip()
        # Ensure the message is under 250 characters to avoid cutting it short
        if len(spam_message) > 250:
            spam_message = spam_message[:247] + "..."
        # Repeat the message as many times as possible without exceeding 500 characters
        repeated_message = (spam_message + " ").rstrip()
        while len(repeated_message + spam_message + " ") <= 500:
            repeated_message += " " + spam_message
        await message.channel.send(repeated_message)
    elif command == "opgg":
        await message.channel.send("ADD OPGG LOOKUPS")
    elif command == "youtube":
        await message.channel.send(
            "Watch Peks' latest video dealdough here: https://www.youtube.com/watch?v=vE0iNgwDl8E ",
        )
    elif command == "cannon":
        cannon_count += 1  # Properly increment the cannon count
        await message.channel.send(f"Cannon count: {cannon_count}")
    elif command == "coin":
        result = "Heads" if random.randint(0, 1) == 0 else "Tails"
        await message.channel.send(
            f"Coin flip? Heads, Peks wins. Tails, you lose. Good luck! {result}",
        )
    elif command == "deadge":
        await message.channel.send(
            "Deadge? Even when Peks is down, he's never out. The comeback king.",
        )
    elif command == "endday":
        await message.channel.send("End of the day? The fun doesn't stop until Peks says so.")
    elif command == "quadra":
        await message.channel.send("Quadra kill! Peks is on fire. Can he get the penta?")
    elif command == "uptime":
        await message.channel.send(
            "Uptime? Peks has been streaming for hours. Time flies when you're having fun!",
        )
    elif command == "about":
        await message.channel.send("Murphy2 is the eventual replacement for MurphyAI. Currently in alpha.")
    elif command == "legend":
        await message.channel.send(
            "Check out Legend of Peks now on Steam. https://store.steampowered.com/app/2529400/Legend_of_Peks/"
        )
    elif command == "addcommmand":
        await message.channel.send("COMMANDS NEED TO BE ADDED MANUALLY FOR NOW.")
    elif command == "copypasta":
        await message.channel.send(
            "Hello everyone welcome back to the chat my dudes how's everyone doing today i myself am doing quite frankly a little weird to be honest because i have just played a game with a rek'sai who was bug abusing now i don't fully understand how this bug works and i also don't really want to be promoting the bug either but i would like to shed some light upon it so that riot might notice it in order to fix it because quite frankly it is absolutely disgusting now there might also be a similar bug with corki from what the rek'sai has told me in game but this video isn't about corki it's about rek'sai now what this bug involves is rek'sai e her burrow unborrow and collector now what the bug actually does is it brings the target down to five percent hp and the weird thing about it is if the target is not killed the target will regen to one hundred persent hp as shown here by the lee sin and the even weirder thing is that the bug can actually proc on rek'sai herself as you can see here as well rek'sai is regening to one hundred percent hp as if she had war mogs without war mogs so it is it is a fucking baffling bug to be honest it is completely game breaking and i am honestly quite baffled at the fact that it's actually in the game now it works on from what i've seen literally everything jungle camps minions champions baron dragon quite literally everything and it is so stupid so yeah i don't know riot please for fuck sake get your shit together fix your damn game and yeah i don't know this is just fuckin stupid but yeah as you can see it works on rek'sai as well uh she just randomly loses like all of her hp apart from five percent and then fully regens it back up i don't know man it's fuckin stupid anyway either way i stream four days a week on down on twitch.tv/ihaspeks so please if you liked the video consider liking subscribing um my videos have been fairly all over the place recently i do apologize about that i i'm i know i've been fairly busy but yeah um yeah do go check out the twitch if you want to see some more live content and with that said do have a good evening good night good sleep and i will talk to all you amazing people next time buh bye"
        )
    else:
        return
