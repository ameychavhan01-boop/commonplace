"""Illustration list. Every prompt = STYLE + scene description, so all images
share one consistent world. Text is added later in code (never by the AI), so
every prompt forbids text, logos and real people.
"""
STYLE = (
    "Flat 2D hand-drawn editorial cartoon illustration in a consistent storybook style: clean bold dark-navy outlines, "
    "warm limited colour palette of cream, warm orange, teal, soft red, mustard yellow and small glowing lime-green accents, "
    "subtle paper texture, soft shading, simple friendly characters with rounded shapes, simple dot eyes and simplified "
    "mitten-like hands, generic invented people only. Wide 16:9 cinematic composition with clear focal point and some empty "
    "space. Absolutely no text, no letters, no numbers, no logos, no brand marks, no watermarks, no real people, no photos."
)

# id: (scene description, where used)
IMAGES = {
 "img01": ("Early morning 7 AM in a cosy bedroom, golden sunlight through the window, a sleepy young adult in pajamas sitting up in bed reaching for a glowing smartphone on the nightstand, alarm clock nearby", "hook"),
 "img02": ("Close-up of two cartoon hands holding a smartphone, the screen shows only an empty grey chat window with a loading spinner, morning light, feeling of confusion", "hook"),
 "img03": ("The same young adult at a small home desk with a laptop and coffee mug, frowning in confusion at a blank laptop screen with a spinning loading circle", "hook"),
 "img04": ("Shocked young adult holding a phone whose screen shows a steep red downward arrow chart, red glow lighting their face, coffee spilling", "hook"),
 "img05": ("A modern city skyline at dawn, in the middle a giant glowing green computer-chip shaped skyscraper is breaking apart into thousands of floating pixel particles and vanishing into the sky, people on the street looking up", "hook, day1"),
 "img06": ("Dramatic dark background: a huge glowing green computer chip in the centre cracking apart with light bursting through the cracks, small pieces flying outward, space on the left and right for a title", "title"),
 "img07": ("One single skilled chef working alone in a small tidy kitchen, carefully cooking one dish at a time, calm and focused", "what"),
 "img08": ("An enormous kitchen hall seen from above with hundreds of tiny identical cooks all chopping vegetables at the same time in neat rows, energetic and busy", "what"),
 "img09": ("Inside a giant data center hall, long rows of tall server racks with blinking green lights stretching into the distance, cool blue and green glow, a tiny technician walking", "what, rebuild"),
 "img10": ("Many different programmers around the world at desks and laptops, connected by glowing lines to one big glowing green chip floating in the centre, as if all speaking the same language to it", "what"),
 "img11": ("Exterior of a giant windowless data center building at night with glowing vents, power lines and cooling towers, a huge warehouse-like building", "what"),
 "img12": ("A city at midnight under a full moon, quiet streets, a big clock tower showing both hands pointing straight up, a large data center building glowing on the edge of town", "hour1"),
 "img13": ("Inside a data center as the lights switch off row by row, server racks going dark from the far end towards the viewer, a single worried technician holding a torch", "hour1, rebuild"),
 "img14": ("A collage of different people around the world (an office worker, a student, an elderly man, a teenager) all staring at phones and laptops showing loading spinners, puzzled faces", "hour1"),
 "img15": ("A digital artist at a drawing tablet with a frozen glitchy half-finished picture on the monitor, hands raised in frustration", "hour1"),
 "img16": ("A kitchen counter with a small smart speaker whose light ring is dark, a person in an apron leaning towards it waiting for an answer that never comes", "hour1"),
 "img17": ("A dark landscape of many data center buildings with their lights off, but one small data center on the right still glowing brightly with its own colourful light", "hour1"),
 "img18": ("A hospital doctor in a white coat looking at a blank computer monitor next to a medical scanner, waiting, a patient on a bed", "hour1"),
 "img19": ("A bank security operations room with many screens gone dark, staff looking confused, a big empty wall display", "hour1"),
 "img20": ("A TV weather presenter standing in front of a completely blank grey weather map screen, awkward smile", "hour1"),
 "img21": ("A scientist in a lab coat and goggles in a laboratory, beside a big screen showing a frozen colourful molecule model, test tubes on the bench", "hour1"),
 "img22": ("A busy stock exchange trading floor at the opening bell, traders in jackets shouting and pointing at big screens full of red downward arrows, papers flying", "day1"),
 "img23": ("A person on a sofa checking an investment app on a phone, the screen shows a pie chart with one slice missing, surprised expression", "day1"),
 "img24": ("Paper money bills blowing away in a strong wind over a city at morning, turning into ash and dust as they fly into the sky", "day1"),
 "img25": ("A long row of giant dominoes falling one after another across a tabletop city, each domino shaped like a small factory or office building", "day1"),
 "img26": ("Crowd of worried investors and office workers looking up at a giant board full of question marks, confused faces", "day1"),
 "img27": ("A glass-walled boardroom high in a skyscraper, a group of generic tech executives in panic, one with head in hands, papers everywhere, phones ringing", "week1"),
 "img28": ("A huge empty loading dock of a warehouse, open shutter doors, an empty conveyor belt and stacks of empty pallets, a worker waiting with a clipboard", "week1"),
 "img29": ("A gigantic chip factory clean room with workers in white bunny suits and robot arms, a long queue of trucks outside waiting, a big wall calendar fully booked", "week1"),
 "img30": ("A tired translator sitting at a tiny desk inside an enormous library with endless towering shelves of books, translating one book at a time by lamp light", "week1"),
 "img31": ("Three rival workers each holding only a few pieces of a giant jigsaw puzzle shaped like a computer machine, the puzzle on the floor is incomplete with big gaps", "week1"),
 "img32": ("An auction room where people in suits are frantically raising paddles to bid on a single small glowing computer chip on a velvet pedestal, price tag flying upwards", "week1"),
 "img33": ("A modern tech office in Bengaluru at night, a diverse team of Indian engineers at desks with chip design diagrams on their monitors, warm desk lamps, city lights through the window", "india"),
 "img34": ("An Indian software engineer in a small apartment, waking up and staring in shock at their phone, morning light, family photo on the wall, chai cup on the table", "india"),
 "img35": ("A small Indian AI startup office with young founders around a table looking sadly at a dark server rack in the corner, sticky notes on the wall", "india"),
 "img36": ("A gigantic AI data center under construction in a dry flat Indian landscape, idle construction cranes, stopped trucks, workers waiting in the shade", "india"),
 "img37": ("A large Indian IT services office floor with rows of desks, a big project board with frozen tasks, a team on a video call with a client who is pressing a big pause button", "india"),
 "img38": ("A happy young person on a crowded Mumbai local train smiling while playing a colourful game on a smartphone, other passengers around", "india"),
 "img39": ("A shocked young PC gamer in an electronics shop staring at a graphics card in a glass case with an enormous price tag (tag shown blank), gaming headset around the neck", "india"),
 "img40": ("Shopkeepers and customers at a busy Indian street market gathered around a small TV showing a falling red stock chart, worried faces", "india"),
 "img41": ("A bright, hopeful sunrise office in India where many engineers are busily rewriting code on screens, sunlight pouring in, energetic and optimistic", "india"),
 "img42": ("A city skyline at sunrise with construction cranes building new factories and towers, rays of hope, birds flying", "rebuild"),
 "img43": ("Inside two rival chip factories working at full speed, conveyor belts full of glowing chips, workers and robot arms hurrying", "rebuild"),
 "img44": ("A giant watering can in the sky pouring golden coins onto a young factory growing like a plant from the ground", "rebuild"),
 "img45": ("Engineers carrying cardboard boxes of belongings walking out of an empty building and being warmly welcomed with handshakes into several other company buildings across the street", "rebuild"),
 "img46": ("A skyline with six different colourful chip-shaped towers of similar height standing side by side, bridges connecting them, balanced and healthy city", "rebuild"),
 "img47": ("A big busy city on an island connected to the mainland by only one single bridge, the bridge packed with traffic, and a crack appearing in the middle of the bridge", "lesson"),
 "img48": ("A designer at a drafting table drawing a large blueprint of a computer chip with rulers and pencils, in a bright design studio with no factory equipment", "lesson"),
 "img49": ("A gigantic semiconductor factory on a coastline across the sea, with ships carrying crates of chips away to the rest of the world", "lesson"),
 "img50": ("A thoughtful person standing in front of a large globe surrounded by many small company buildings orbiting it, one hand on chin, a big question-mark-shaped cloud above", "lesson"),
 "img51": ("A cosy creator desk at night with a desk lamp, a small globe, a notebook and a coffee mug, with lots of empty space on the left and right sides", "endscreen"),
}

THUMBNAIL = ("Right half of the image: one big expressive cartoon character (young adult, wide eyes, mouth open in shock, "
             "hands on cheeks) next to a large glowing green computer chip that is cracking apart and disappearing into pixels, "
             "red light bursting through the cracks. Left half of the image: plain dark navy background with a soft warm glow and "
             "nothing else (reserved for title text). Very high contrast, bold and simple, readable at small size")
