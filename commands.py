async def handle_command(bot, message):
    command = message.content[len(bot.prefix):].split(' ')[0]

    if command == 'commands':
        await bot.send_message(message.channel, "Available commands: ?join, ?leave, ?q, ?here, ?nothere, !ai <message>")
    elif command == 'ping':
        await bot.send_message(message.channel, "Pong!")

    elif command == 'bald':
            await bot.send_message(message.channel, "Looks like Peks forgot his wig today!")
    elif command == 'int':
            await bot.send_message(message.channel, "Peks is practicing his diving skills in-game, don't mind the score.")
    elif command == 'tea':
            await bot.send_message(message.channel, "It's always tea time when you're watching Peks. Earl Grey or Green?")
    elif command == 'coffee':
            await bot.send_message(message.channel, "Peks prefers his coffee like his gameplay, dark and intense.")
    elif command == 'bestbot':
            await bot.send_message(message.channel, "I'm flattered, but we all know Peks is the real MVP here.")
    elif command == 'garen':
            await bot.send_message(message.channel, "DEMACIA! Oops, wrong game. Peks still loves spinning to win though.")
    elif command == 'jam':
            await bot.send_message(message.channel, "Time to jam out! Peks has the best playlists for gaming.")
    elif command == 'masters':
            await bot.send_message(message.channel, "Masters? Easy. Peks is on his way, just a few... hundred games more.")
    elif command == 'milkpasta':
            await bot.send_message(message.channel, "Peks's secret recipe. Don't knock it till you try it!")
    elif command == 'bye':
            await bot.send_message(message.channel, "See you next time! Peks will miss you!")
    elif command == 'smelly':
            await bot.send_message(message.channel, "Whoa, whoa. Peks took a shower... last week. Promise!")
    elif command == 'robinvroom':
            await bot.send_message(message.channel, "The legend says if you say his name three times, Peks will start playing racing games.")
    elif command == 'slingshot':
            await bot.send_message(message.channel, "Peks's favorite way to start a game. Watch out for those surprise attacks!")
    elif command == 'iloveu':
            await bot.send_message(message.channel, "Awww, Peks loves you too! Group hug!")
    elif command == 'brb':
            await bot.send_message(message.channel, "Peks will be right back, probably grabbing more snacks.")
    elif command == '4':
            await bot.send_message(message.channel, "Four what? Wins in a row? Deaths? The mystery continues.")
    elif command == 'laws':
            await bot.send_message(message.channel, "The only law here is to have fun and be kind. And always listen to Peks.")
    elif command == 'returned':
            await bot.send_message(message.channel, "Like a boomerang, Peks always comes back. You can't get rid of him that easily.")
    elif command == 'flauenn':
            await bot.send_message(message.channel, "A secret code? Maybe it's the password to Peks's heart.")
    elif command == 'song':
            await bot.send_message(message.channel, "Now playing: Peks's victory anthem. Sing along!")
    elif command == 'raidmsg':
            await bot.send_message(message.channel, "Raiders welcome! You're just in time for the Peks show.")
    elif command == 'mad':
            await bot.send_message(message.channel, "Mad? Never. Peks is the epitome of calm and collected. *Table flip*")
    elif command == '4song':
            await bot.send_message(message.channel, "A song for every occasion, especially the fourth one.")
    elif command == 'roan':
            await bot.send_message(message.channel, "Roan? A mysterious ally or perhaps a formidable foe in Peks's adventures.")
    elif command == 'Roan':
            await bot.send_message(message.channel, "Capital R Roan, definitely someone important. Or maybe Peks just hit caps lock.")
    elif command == 'schedule':
            await bot.send_message(message.channel, "Peks's schedule is packed with fun, games, and the occasional unexpected nap.")
    elif command == 'scream':
            await bot.send_message(message.channel, "AHHHH! Just kidding, Peks is too cool to scream. Or is he?")
    elif command == 'blob':
            await bot.send_message(message.channel, "Blobbing around with Peks. It's more fun than it sounds.")
    elif command == 'dj':
            await bot.send_message(message.channel, "DJ Peks in the house! Dropping beats and epic gameplay.")
    elif command == '1':
            await bot.send_message(message.channel, "Number one in our hearts and occasionally in the game.")
    elif command == 'XD':
            await bot.send_message(message.channel, "XD indeed. Peks's streams are full of laughs and good times.")
    elif command == 'shane':
            await bot.send_message(message.channel, "Shane? Oh, you mean Peks's alter ego when he's feeling extra mysterious.")
    elif command == 'birthday':
            await bot.send_message(message.channel, "Happy Birthday! Peks has a special cake just for you. It's virtual, but it's the thought that counts.")
    elif command == 'ratbucket':
            await bot.send_message(message.channel, "Ratbucket? A secret operation or Peks's snack stash? The world may never know.")
    elif command == 'caedrel':
            await bot.send_message(message.channel, "Caedrel? Sounds like a champion Peks would main... if he existed in his games.")
    elif command == 'info':
            await bot.send_message(message.channel, "Looking for info? Peks's life is an open book. Mostly.")
    elif command == 'π':
            await bot.send_message(message.channel, "3.14159... Peks's favorite number because it's as endless as his content.")
    elif command == 'emotesnotspam':
            await bot.send_message(message.channel, "Emotes = expression. Spam them to show your love for Peks!")
    elif command == 'works':
            await bot.send_message(message.channel, "It works! Just like Peks's charm. 60% of the time, it works every time.")
    elif command == 'bestcheese':
            await bot.send_message(message.channel, "The best cheese? Peks's gameplay. Just kidding, it's Gouda.")
    elif command == 'rgbjam':
            await bot.send_message(message.channel, "RGB Jam, for when you need your music to be as colorful as your lighting.")
    elif command == '8ball':
            await bot.send_message(message.channel, "Magic 8-ball says: Definitely! Peks agrees.")
    elif command == 'forgore':
            await bot.send_message(message.channel, "Forgore? Peks never forgets... except when he does.")
    elif command == 'quotes':
            await bot.send_message(message.channel, "Peks's quotes: 'If at first you don't succeed, blame the lag.'")
    elif command == 'elo':
            await bot.send_message(message.channel, "ELO? It's not just a number, it's a state of mind. Peks's state is 'chill'.")
    elif command == 'update_queue':
            await bot.send_message(message.channel, "Queue updated. Your patience is appreciated, just like Peks's gameplay.")
    elif command == 'lurk':
            await bot.send_message(message.channel, "Lurkers welcome! Peks appreciates your silent support.")
    elif command == 'e':
            await bot.send_message(message.channel, "E. That's it. That's the message.")
    elif command == 'leaf':
            await bot.send_message(message.channel, "Leaf it to Peks to turn over a new leaf every stream.")
    elif command == 'server':
            await bot.send_message(message.channel, "Server? More like serv-her another win, am I right?")
    elif command == 'anime':
            await bot.send_message(message.channel, "Anime night with Peks? Count me in! What are we watching?")
    elif command == 'tiktok':
            await bot.send_message(message.channel, "TikTok on the clock, but the party don't stop, no. Peks's streams are just as catchy.")
    elif command == 'cheer':
            await bot.send_message(message.channel, "Give me a P! Give me an E! Give me a K! Give me an S! What does that spell? PEKS!")
    elif command == 'rugo':
            await bot.send_message(message.channel, "Rugo? Sounds like a new character in Peks's gaming universe.")
    elif command == 'teiva':
            await bot.send_message(message.channel, "Teiva, the unsung hero of Peks's streams. Always there, always supportive.")
    elif command == 'idea':
            await bot.send_message(message.channel, "Got an idea? Peks is all ears. As long as it involves gaming or snacks.")
    elif command == 'squat':
            await bot.send_message(message.channel, "Squat challenge! Peks is doing one for every sub. Feel the burn!")
    elif command == 'subathon':
            await bot.send_message(message.channel, "Subathon time! The longer you sub, the longer Peks streams. It's a win-win!")
    elif command == 'subtimer':
            await bot.send_message(message.channel, "Sub timer is ticking! Every sub adds time to the stream. How long can we go?")
    elif command == 'bracket':
            await bot.send_message(message.channel, "Bracket? You're in Peks's league now. Good luck!")
    elif command == 'pilk':
            await bot.send_message(message.channel, "Pilk? Peks's favorite drink. It's... unique.")
    elif command == 'video':
            await bot.send_message(message.channel, "New video alert! Peks has uploaded another masterpiece. Go check it out!")
    elif command == 'chatplaylist':
            await bot.send_message(message.channel, "Chat's playlist is now playing. Peks has the best DJ's in town.")
    elif command == 'flash':
            await bot.send_message(message.channel, "Flash? More like flash of genius. Peks's plays are out of this world.")
    elif command == 'cousin':
            await bot.send_message(message.channel, "Cousin? Oh, you must mean Peks's sidekick in his latest gaming adventure.")
    elif command == '1kfollower':
            await bot.send_message(message.channel, "1k followers! Peks couldn't have done it without you. Here's to 1k more!")
    elif command == 'tails':
            await bot.send_message(message.channel, "Tails never fails. Except when Peks is flipping the coin. Then it's anyone's guess.")
    elif command == 'tanked':
            await bot.send_message(message.channel, "Tanked? Peks prefers the term 'strategically positioned at the bottom of the leaderboard'.")
    elif command == 'crazy':
            await bot.send_message(message.channel, "Crazy? Peks's streams are a good kind of crazy. The best kind, actually.")
    elif command == 'cousins':
            await bot.send_message(message.channel, "Cousins? More like co-conspirators in Peks's gaming escapades.")
    elif command == 'art':
            await bot.send_message(message.channel, "Art stream! Watch Peks create masterpieces or... something close to it.")
    elif command == 'q':
            await bot.send_message(message.channel, "Q? Quick, someone tell Peks it's his cue!")
    elif command == 'emoteslink':
            await bot.send_message(message.channel, "Looking for emotes? Here's the link to express your Peks love in chat.")
    elif command == 'jele':
            await bot.send_message(message.channel, "Jele? A rare delicacy in Peks's stream. Best served with humor and good vibes.")
    elif command == 'cs':
            await bot.send_message(message.channel, "CS? In Peks's world, it stands for 'Constantly Smiling'.")
    elif command == 'uwu':
            await bot.send_message(message.channel, "UwU, what's this? Another adorable moment on Peks's stream.")
    elif command == 'nothing':
            await bot.send_message(message.channel, "Nothing? Not on Peks's watch. There's always something happening here.")
    elif command == 'top':
            await bot.send_message(message.channel, "Top? Peks is always on top of his game. Except when he's not.")
    elif command == 't':
            await bot.send_message(message.channel, "T for Tryhard. Peks's middle name when it comes to gaming.")
    elif command == '9ball':
            await bot.send_message(message.channel, "9-ball? Peks is a pool shark. Beware if he challenges you to a game.")
    elif command == 'here':
            await bot.send_message(message.channel, "You're here! And so is Peks. It's going to be a good day.")
    elif command == 'subs':
            await bot.send_message(message.channel, "Subs, assemble! Your support makes Peks's day, every day.")
    elif command == 'discord':
            await bot.send_message(message.channel, "Join Peks's Discord for more fun and games off-stream. See you there!")
    elif command == 'vid':
            await bot.send_message(message.channel, "Vid? Peks has plenty. Check out his latest uploads for a good time.")
    elif command == 'join':
            await bot.send_message(message.channel, "Join the fun! Peks welcomes all to his stream. The more, the merrier.")
    elif command == 'scam':
            await bot.send_message(message.channel, "Scam? The only scam here is how addictively fun Peks's streams are.")
    elif command == 'weather':
           await bot.send_message(message.channel, "Weather report: It's always sunny in Peks's stream. Bring sunglasses.")
    elif command == 'penta':
            await bot.send_message(message.channel, "Penta kill! Oh wait, that was just Peks dreaming again.")
    elif command == 'latege':
            await bot.send_message(message.channel, "Latege? More like latte, because Peks is always caffeinated and ready to go.")
    elif command == 'joke':
            await bot.send_message(message.channel, "Want to hear a joke? Peks's KDA. Just kidding, he's actually pretty good.")
    elif command == 'truth':
            await bot.send_message(message.channel, "The truth? You can't handle the truth! But Peks will tell you anyway.")
    elif command == 'spam':
            await bot.send_message(message.channel, "Spam in chat? Only if it's love spam for Peks.")
    elif command == 'nothere':
            await bot.send_message(message.channel, "Not here? Peks will notice. He misses you already.")
    elif command == 'teams':
            await bot.send_message(message.channel, "Teams? Peks is a one-man army. But he appreciates his squad.")
    elif command == 'opgg':
            await bot.send_message(message.channel, "OP.GG? More like OP.PEKS. Check out those stats!")
    elif command == 'youtube':
            await bot.send_message(message.channel, "YouTube? Yeah, Peks is there too. Subscribe for epic content.")
    elif command == 'cannon':
            await bot.send_message(message.channel, "Cannon? Peks is more of a 'charge in headfirst' kind of player.")
    elif command == 'coin':
            await bot.send_message(message.channel, "Coin flip? Heads, Peks wins. Tails, you lose. Good luck!")
    elif command == 'deadge':
            await bot.send_message(message.channel, "Deadge? Even when Peks is down, he's never out. The comeback king.")
    elif command == 'endday':
            await bot.send_message(message.channel, "End of the day? The fun doesn't stop until Peks says so.")
    elif command == 'accept_share':
            await bot.send_message(message.channel, "Accepting and sharing? That's what Peks's community is all about.")
    elif command == 'leave':
            await bot.send_message(message.channel, "Leaving so soon? Peks will be here, waiting for your return.")
    elif command == 'commands':
            await bot.send_message(message.channel, "Looking for commands? You've found them. Try ?bald, ?int, ?tea... and many more!")
    elif command == 'quadra':
            await bot.send_message(message.channel, "Quadra kill! Peks is on fire. Can he get the penta?")
    elif command == 'Q':
            await bot.send_message(message.channel, "Q? Quick, someone tell Peks it's his cue!")
    elif command == 'uptime':
            await bot.send_message(message.channel, "Uptime? Peks has been streaming for hours. Time flies when you're having fun!")
    else:
        await bot.send_message(message.channel, "Unknown command. Type ?help for a list of commands.")
