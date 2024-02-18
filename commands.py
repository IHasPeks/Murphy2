import random

async def handle_command(bot, message):
    command = message.content[len(bot.prefix) :].split(" ")[0]

    if command == "commands":
        await bot.send_message(
            message.channel,
            "Available commands:?ping ?bald ?int ?tea ?coffee ?bestbot ?garen ?jam ?masters ?milkpasta ?bye ?smelly ?robinvroom ?slingshot ?iloveu ?brb ?4 ?laws ?returned ?flauenn ?song ?raidmsg ?mad ?4song ?roan ?Roan ?schedule ?scream ?blob ?dj ?1 ?XD ?shane ?birthday ?ratbucket ?caedrel ?info ?π ?emotesnotspam ?works ?bestcheese ?rgbjam ?8ball ?forgore ?quotes ?elo ?update_queue ?lurk ?e ?leaf ?server ?anime ?tiktok ?cheer ?rugo ?teiva ?idea ?squat ?subathon ?subtimer ?bracket ?pilk ?video ?chatplaylist 11:32 MurphyAI: flash ?cousin ?1kfollower ?tails ?tanked ?crazy ?cousins ?art ?q ?emoteslink ?jele ?cs ?uwu ?nothing ?top ?t ?9ball ?here ?subs ?discord ?vid ?join ?scam ?weather ?penta ?latege ?joke ?truth ?spam ?nothere ?teams ?opgg ?youtube ?cannon ?coin ?deadge ?endday ?accept_share ?leave ?commands ?quadra ?Q ?uptime ",
        )
    elif command == "ping":
        await bot.send_message(message.channel, "Pong!")
    elif command == "bald":
        await bot.send_message(message.channel, "Looks like Peks forgot his wig today!")
    elif command == "int":
        await bot.send_message(
            message.channel,
            "Peks is practicing his diving skills in-game, don't mind the score. KEKW",
        )
    elif command == "tea":
        await bot.send_message(
            message.channel,
            "Peks prefers his tea like his gameplay, dark and intense. PauseChamp",
        )
    elif command == "bestbot":
        await bot.send_message(
            message.channel,
            "I'm flattered, but we all know Peks is the real MVP here. NOT... I AM THE BEST BOT elmoFire ",
        )
    elif command == "garen":
        await bot.send_message(
            message.channel,
            "DEMACIA! garen gaming Garen Peks loves spinning to win. garenPog",
        )
    elif command == "jam":
        await bot.send_message(
            message.channel,
            "blobSlide blobSlide blobSlide ratJAM blobDance ratJAM GroupJAM blobDance catJAM pepeJam pepeJAMJAMJAM pepeJAMJAMJAM pepeJam AMOGUS AMOGUS AMOGUS dogePLS dogePLS dogePLS dogePLS dogePLS dogJAM dogJAM GroupJAM BANGER BANGER BANGER GroupJAM GroupJAM ",
        )
    elif command == "pog":
        await bot.send_message(
            message.channel, "Pog? Peks is the definition of Pog. PogChamp"
        )
    elif command == "masters":
        await bot.send_message(
            message.channel,
            "Masters? Easy. Peks is on his way, just a few... hundred games more.",
        )
    elif command == "milkpasta":
        await bot.send_message(
            message.channel, "Peks's secret recipe. Don't knock it till you try it!"
        )
    elif command == "bye":
        await bot.send_message(
            message.channel,
            f"{message.author.mention} is leaving, Peks will probably miss you.",
        )
    elif command == "smelly":
        await bot.send_message(
            message.channel,
            "Whoa, whoa. Peks took a shower... last week. Do rats even take showers!",
        )
    elif command == "robinvroom":
        await bot.send_message(
            message.channel,
            "https://clips.twitch.tv/AltruisticEnergeticMochaPicoMause-VJCUTug58An6d2JM ",
        )
    elif command == "slingshot":
        await bot.send_message(
            message.channel,
            "https://clips.twitch.tv/DignifiedHelpfulTruffleYouDontSay-mCxDlAu3CJdz87pr",
        )
    elif command == "iloveu":
        await bot.send_message(
            message.channel,
            "https://clips.twitch.tv/CleverPowerfulAnacondaShazBotstix-obqsk2mZb_CN_G2i",
        )
    elif command == "brb":
        await bot.send_message(
            message.channel,
            f"{message.author.mention} will be right back, probably grabbing more snacks.",
        )
    elif command == "4":
        await bot.send_message(
            message.channel,
            "A GIGACHAD 5Head big brain person who helps me find bugs, AND who also edits emotes",
        )
    elif command == "laws":
        await bot.send_message(
            message.channel, "1. Eat Pizza 2. Spell it alwase 3. Don't play runescape"
        )
    elif command == "returned":
        await bot.send_message(
            message.channel, f"{message.author.mention} is back, yippee"
        )
    elif command == "flauenn":
        await bot.send_message(message.channel, "Chatting")
    elif command == "song":
        await bot.send_message(
            message.channel, "https://www.youtube.com/watch?v=dQw4w9WgXcQ "
        )
    elif command == "raidmsg":
        await bot.send_message(
            message.channel,
            "ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ihaspeKid ihaspePet ihaspeBounce ihaspeKid ihaspePet BALD DOGGO RAID ihaspeBounce ",
        )
    elif command == "mad":
        await bot.send_message(
            message.channel,
            "TrollFace mad? Never. Peks is the epitome of calm and collected. *Table flip*",
        )
    elif command == "4song":
        await bot.send_message(
            message.channel, "https://www.youtube.com/watch?v=u8ccGjar4Es"
        )
    elif command == "roan":
        await bot.send_message(message.channel, "Woan is vewy UwU Gayge PogPlanting")
    elif command == "Roan":
        await bot.send_message(
            message.channel,
            "you have found Roan's secret command. Roan is amazing peepoLove UwU",
        )
    elif command == "schedule":
        await bot.send_message(
            message.channel,
            "https://cdn.discordapp.com/attachments/949012582595964958/1155562279367098508/chedule_1.png?ex=65db7e3c&is=65c9093c&hm=d81efc1bfa547d89165a731363578564684ab1aad849a01d6cc3b8eb118cb224&",
        )
    elif command == "scream":
        await bot.send_message(
            message.channel,
            "AHHHH! Just kidding, Peks is too cool to scream. Or is he just a little girl?",
        )
    elif command == "blob":
        await bot.send_message(
            message.channel,
            "Blobbing around with Peks. It's more fun than it sounds. blobSlide blobSlide blobSlide ratJAM blobDance ratJAM GroupJAM blobDance catJAM pepeJam pepeJAMJAMJAM pepeJAMJAMJAM pepeJam AMOGUS AMOGUS AMOGUS dogePLS dogePLS dogePLS dogePLS dogePLS dogJAM dogJAM GroupJAM BANGER BANGER BANGER GroupJAM GroupJAM",
        )
    elif command == "1":
        await bot.send_message(
            message.channel, "Number one in our hearts and occasionally in the game."
        )
    elif command == "XD":
        await bot.send_message(message.channel, "XD indeed. TrollFace mad?XD")
    elif command == "shane":
        await bot.send_message(message.channel, "shane found a bug in discord POGGERS ")
    elif command == "birthday":
        await bot.send_message(
            message.channel, "https://www.youtube.com/watch?v=wC4y4b8iyR0"
        )
    elif command == "ratbucket":
        await bot.send_message(
            message.channel, "One day peks will get into the ratbucket Ratge ihaspeDerp"
        )
    elif command == "caedrel":
        await bot.send_message(
            message.channel,
            "https://clips.twitch.tv/GentleNimbleStarPrimeMe-sZRWuCU6llKgbAlh",
        )
    elif command == "info":
        await bot.send_message(
            message.channel,
            "Looking for info? Peks's life is an open book. Mostly. Just ask him any question and he will be sure to not answer",
        )
    elif command == "pi":
        await bot.send_message(
            message.channel,
            "3.14159... Peks's favorite number because it's the number of seconds he's spent on a grey screen on league.",
        )
    elif command == "emotesnotspam":
        await bot.send_message(
            message.channel, "https://betterttv.com/users/6024310f0b26f21727617c8f"
        )
    elif command == "works":
        await bot.send_message(
            message.channel,
            "It works! Just like Peks's charm. 60% of the time, it works every time.",
        )
    elif command == "bestcheese":
        await bot.send_message(
            message.channel,
            "The best cheese? Peks's gameplay. Just kidding, it's Feta.",
        )
    elif command == "rgbjam":
        await bot.send_message(
            message.channel,
            "RGB Jam, for when you need your music to be as colorful as your lighting. blobDance blobDance blobDance blobDance blobSlide blobSlide blobSlide blobSlide blobSlide peepoDJ blobDance peepoDJ blobDance peepoDJ blobDance peepoDJ raveDumper peepoDJ raveDumper peepoDJ raveDumper peepoDJ skeletonDance peepoDJ skeletonDance peepoDJ Danceboye Danceboye Danceboye Danceboye peepoDJ peepoDJ peepoDJ peepoDJ peepoDJ peepoDJ peepoDJ ",
        )
    elif command == "8ball":
        await bot.send_message(
            message.channel, "Magic 8-ball says: Definitely! Peks agrees."
        )
    elif command == "forgore":
        await bot.send_message(
            message.channel,
            "I FORGORR ☠ ☠ ☠ ☠ ☠? Peks never forgets... except when he does.",
        )
    elif command == "quotes":
        await bot.send_message(
            message.channel,
            "'If at first you don't succeed, blame the lag.'6Head -Peks ",
        )
    elif command == "elo":
        await bot.send_message(
            message.channel,
            "ELO? It's not just a number, it's a state of mind. Peks is currently Dogshit III 75 LP on this account.",
        )
    elif command == "lurk":
        await bot.send_message(
            message.channel,
            f"{message.author.mention} is lurking, Peks appreciates your silent support. dogeLurk",
        )
    elif command == "e":
        await bot.send_message(
            message.channel,
            "Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE Dance myEE ",
        )
    elif command == "leaf":
        await bot.send_message(
            message.channel,
            "Leaf it to Peks to turn over a new leaf every stream. Leaf",
        )
    elif command == "server":
        await bot.send_message(
            message.channel, "Server? More like serv-her another win, am I right?"
        )
    elif command == "anime":
        await bot.send_message(
            message.channel,
            "Muercie is officially an anime enjoyer. time for an anime night with Peks? What are we watching?",
        )
    elif command == "tiktok":
        await bot.send_message(
            message.channel,
            "TikTok on the clock, but the party don't stop. https://www.tiktok.com/@ihaspeks .",
        )
    elif command == "cheer":
        await bot.send_message(
            message.channel,
            "Give me a P! Give me an E! Give me a K! Give me an S! What does that spell? peepoCheer P peepoCheer E peepoCheer K peepoCheer S peepoCheer",
        )
    elif command == "rugo":
        await bot.send_message(
            message.channel, "Rugo? Actually i wonder where he went?"
        )
    elif command == "teiva":
        await bot.send_message(
            message.channel,
            "Teiva, Gayge the unsung hero of Peks's streams. Always there, always supportive.",
        )
    elif command == "idea":
        await bot.send_message(
            message.channel,
            "Got an idea? Peks is all ears. As long as it involves gaming or snacks. dogeHead",
        )
    elif command == "squat":
        await bot.send_message(
            message.channel,
            "Squat challenge! Peks is doing one for every sub. Feel the burn! DOGEDANCE S DOGEDANCE Q DOGEDANCE U DOGEDANCE A DOGEDANCE T DOGEDANCE S DOGEDANCE ",
        )
    elif command == "subathon":
        await bot.send_message(
            message.channel,
            "Ding SubRATathon on the 1st of july. Multiple activities and events. 1v1 and 2v2 tournament -- JOIN THE DISCORD with the command ?discord -- Other events, such as Bingo, Customs, Spoopy games and much much more. Don't forget to join discord to be updated and learn more --- USE THE COMMAND ?discord Ding",
        )
    elif command == "rugothon":
        await bot.send_message(
            message.channel,
            "Ding SubRUGOthon on the 1st of july. Multiple activities and events. 1v1 and 2v2 rugo rumble -- JOIN THE RUGOCORD with the command ?rugocord -- Other events, such as Rugy Bingo, Rugo Customs, Spooky Rugo games and much much more. Don't forget to join rugocord to be updated and learn more --- USE THE COMMAND ?rugocord Ding",
        )
    elif command == "crazy":
        await bot.send_message(
            message.channel,
            "Crazy? i was crazy once. i locked myself in a room, a concrete room, a concrete room with chat, my chat is full of rats which make me crazy",
        )
    elif command == "pilk":
        await bot.send_message(
            message.channel,
            "Pilk? Peks's favorite drink. It's... unique. i hear Muercie is officially a pilk enjoyer",
        )
    elif command == "video":
        await bot.send_message(
            message.channel,
            "New video alert! Peks has uploaded another masterpiece. Go check it out. https://www.youtube.com/watch?v=vE0iNgwDl8E ",
        )
    elif command == "chatplaylist":
        await bot.send_message(message.channel, "https://youtu.be/OryF8smba2A")
    elif command == "flash":
        await bot.send_message(message.channel, "Thats an NA flash there bro KEKW ")
    elif command == "cousin":
        await bot.send_message(
            message.channel,
            "okayCousin BedgeCousin comfycousin CoolCousin cousin cousins cousint FarAwayCousin HeyCousin MadCousin POGCousin SadCousin StrongCousin WeirdCousin WeirdPizzaCousin zazacousin ratin CuteCousin WeirdCousingers ",
        )
    elif command == "1kfollower":
        await bot.send_message(
            message.channel,
            "1k followers! Peks couldn't have done it without you. Here's to 1k more! ItsChrisyBaby was the 1000th follower BASED",
        )
    elif command == "tails":
        await bot.send_message(
            message.channel,
            "tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL tail ihaspeTail ihaspeTailR tailL ",
        )
    elif command == "tanked":
        await bot.send_message(
            message.channel,
            "Tanked? Peks prefers the term 'strategically positioned at the bottom of the leaderboard' https://clips.twitch.tv/BusyHorribleWombatBlargNaut-OQYkzliVdYHyFnj4 .",
        )
    elif command == "cousins":
        await bot.send_message(
            message.channel,
            "okayCousin BedgeCousin comfycousin CoolCousin cousin cousins cousint FarAwayCousin HeyCousin MadCousin POGCousin SadCousin StrongCousin WeirdCousin WeirdPizzaCousin zazacousin ratin ",
        )
    elif command == "art":
        await bot.send_message(
            message.channel,
            "yes peks is actively looking for any kind of commissions please tell him all about it Tomfoolery",
        )
    elif command == "emoteslink":
        await bot.send_message(
            message.channel,
            "Looking for emotes? Here's the link to express your Peks love in chat: 7TV link: https://7tv.app/emote-sets/645c2a418e6b5a947a6131c7 BetterTTV link: https://betterttv.com/users/6024310f0b26f21727617c8f ",
        )
    elif command == "jele":
        await bot.send_message(
            message.channel,
            "Jele? A rare delicacy in Peks's stream. Best served with humor and good vibes. https://imgur.com/a/LbpVdxF ",
        )
    elif command == "cs":
        await bot.send_message(
            message.channel,
            "CS? In Peks's world, it stands for 'Constantly Smiling' https://imgur.com/a/lWCWvER .",
        )
    elif command == "uwu":
        await bot.send_message(
            message.channel,
            "UwU, what's this?!?1 Anyothew adowabwe moment on Peks's stweam.",
        )
    elif command == "nothing":
        await bot.send_message(message.channel, "")
    elif command == "top":
        await bot.send_message(
            message.channel,
            "Top? Peks is always on top of his game. Except when he's not.",
        )
    elif command == "t":
        await bot.send_message(
            message.channel,
            "T for Tryhard. Peks's middle name when it comes to gaming.",
        )
    elif command == "9ball":
        await bot.send_message(message.channel, "what is 9ball? use ?8ball instead")
    elif command == "subs":
        await bot.send_message(
            message.channel, "Subs, assemble! Your support makes Peks's day, every day."
        )
    elif command == "discord":
        await bot.send_message(
            message.channel,
            "Join Peks's Discord for more fun and games off-stream. See you there!: REPLACE THIS WITH DISCORD LINK",
        )
    elif command == "vid":
        await bot.send_message(
            message.channel,
            "Vid? Peks has plenty. Check out his newest video that is 2 years old.",
        )
    elif command == "scam":
        await bot.send_message(
            message.channel,
            "Scam? The only scam here is how addictively fun Peks's streams are. KEKW",
        )
    elif command == "weather":
        await bot.send_message(
            message.channel,
            "Weather report: It's always sunny in Peks's stream. Bring sunglasses.",
        )
    elif command == "penta":
        await bot.send_message(
            message.channel, "Penta kill! Oh wait, that was just Peks dreaming again."
        )
    elif command == "latege":
        await bot.send_message(message.channel, "ADD LATEGE TIMER HERE")
    elif command == "joke":
        await bot.send_message(message.channel, "we are not bringing this back...")
    elif command == "truth":
        await bot.send_message(
            message.channel,
            "The truth? You can't handle the truth! But Peks will tell you anyway.",
        )
    elif command == "spam":
        # Extract the message to spam, removing the command part
        spam_message = message.content[len(bot.prefix) + len(command) + 1:].strip()
        # Repeat the message 5 times as an example, you can adjust the number as needed
        repeated_message = (spam_message + " ") * 999
        await bot.send_message(message.channel, repeated_message)
    elif command == "opgg":
        await bot.send_message(message.channel, "ADD OPGG LOOKUPS")
    elif command == "youtube":
        await bot.send_message(
            message.channel,
            "Watch Peks' latest video dealdough here: https://www.youtube.com/watch?v=vE0iNgwDl8E ",
        )
        # Add a global variable to keep track of the cannon count
        cannon_count = 0

        async def handle_command(bot, message):
            global cannon_count  # Use the global variable inside the function
            command = message.content[len(bot.prefix) :].split(" ")[0]

    elif command == "cannon":
        cannon_count += 1  # Increment the cannon count
        await bot.send_message(message.channel, f"Cannon count: {cannon_count}")
    elif command == "coin":
        result = "Heads" if random.randint(0, 1) == 0 else "Tails"
        await bot.send_message(
            message.channel,
            f"Coin flip? Heads, Peks wins. Tails, you lose. Good luck! {result}",
        )
    elif command == "deadge":
        await bot.send_message(
            message.channel,
            "Deadge? Even when Peks is down, he's never out. The comeback king.",
        )
    elif command == "endday":
        await bot.send_message(
            message.channel, "End of the day? The fun doesn't stop until Peks says so."
        )
    elif command == "quadra":
        await bot.send_message(
            message.channel, "Quadra kill! Peks is on fire. Can he get the penta?"
        )
    elif command == "uptime":
        await bot.send_message(
            message.channel,
            "Uptime? Peks has been streaming for hours. Time flies when you're having fun!",
        )
    else:
        await bot.send_message(
            message.channel, "Unknown command. Type ?help for a list of commands."
        )
