#!/usr/bin/env python3
"""Spyfall — single-port HTTP + WebSocket server.

Run:  python3 server.py
Open: http://localhost:3000
"""
import asyncio
import json
import os
import random
import secrets
import socket
import time
from http import HTTPStatus
from pathlib import Path

from websockets.asyncio.server import serve
from websockets.datastructures import Headers
from websockets.http11 import Response

PORT = int(os.environ.get("PORT", "3000"))
PUBLIC = (Path(__file__).parent / "public").resolve()

LOCATIONS = [
    {"id":"airplane","name":"Airplane","emoji":"✈️","pack":"classic","roles":["First Class Passenger","Air Marshal","Mechanic","Pilot","Flight Attendant","Co-Pilot","Customs Agent","Stewardess"]},
    {"id":"bank","name":"Bank","emoji":"🏦","pack":"classic","roles":["Armored Car Driver","Manager","Consultant","Customer","Robber","Security Guard","Teller","Cashier"]},
    {"id":"beach","name":"Beach","emoji":"🏖️","pack":"outdoor","roles":["Beach Waitress","Kite Surfer","Lifeguard","Photographer","Thief","Vacationer","Sunbather","Ice Cream Truck Driver"]},
    {"id":"casino","name":"Casino","emoji":"🎰","pack":"classic","roles":["Bartender","Head Security Guard","Bouncer","Manager","Hustler","Dealer","Gambler","Waitress"]},
    {"id":"cathedral","name":"Cathedral","emoji":"⛪","pack":"classic","roles":["Priest","Beggar","Sinner","Tourist","Sponsor","Choir Singer","Parishioner","Organist"]},
    {"id":"circus","name":"Circus Tent","emoji":"🎪","pack":"classic","roles":["Acrobat","Animal Trainer","Magician","Visitor","Fire Eater","Clown","Juggler","Ringmaster"]},
    {"id":"corp_party","name":"Corporate Party","emoji":"🥂","pack":"classic","roles":["Entertainer","Manager","Owner","Secretary","Accountant","Delivery Boy","Unwelcome Guest","CEO"]},
    {"id":"crusade","name":"Crusader Army","emoji":"⚔️","pack":"outdoor","roles":["Monk","Imprisoned Saracen","Servant","Bishop","Squire","Archer","Knight","Cook"]},
    {"id":"day_spa","name":"Day Spa","emoji":"💆","pack":"classic","roles":["Customer","Stylist","Masseuse","Manicurist","Makeup Artist","Beautician","Receptionist","Owner"]},
    {"id":"embassy","name":"Embassy","emoji":"🏛️","pack":"classic","roles":["Ambassador","Government Official","Tourist","Refugee","Security Guard","Secretary","Diplomat","Visitor"]},
    {"id":"hospital","name":"Hospital","emoji":"🏥","pack":"classic","roles":["Nurse","Doctor","Anesthesiologist","Intern","Patient","Therapist","Surgeon","Janitor"]},
    {"id":"hotel","name":"Hotel","emoji":"🏨","pack":"classic","roles":["Doorman","Security Guard","Manager","Housekeeper","Customer","Bartender","Bellhop","Receptionist"]},
    {"id":"military","name":"Military Base","emoji":"🪖","pack":"outdoor","roles":["Deserter","Colonel","Medic","Soldier","Sniper","Officer","Tank Engineer","Sergeant"]},
    {"id":"movie_studio","name":"Movie Studio","emoji":"🎬","pack":"classic","roles":["Stuntman","Sound Engineer","Cameraman","Director","Costume Artist","Actor","Make-up Artist","Producer"]},
    {"id":"ocean_liner","name":"Ocean Liner","emoji":"🛳️","pack":"outdoor","roles":["Rich Passenger","Cook","Captain","Bartender","Musician","Waiter","Mechanic","Cruise Director"]},
    {"id":"passenger_train","name":"Passenger Train","emoji":"🚆","pack":"classic","roles":["Mechanic","Border Patrol","Train Attendant","Passenger","Restaurant Chef","Engineer","Stoker","Conductor"]},
    {"id":"pirate_ship","name":"Pirate Ship","emoji":"🏴‍☠️","pack":"outdoor","roles":["Cook","Sailor","Slave","Cannoneer","Bound Prisoner","Cabin Boy","Brave Captain","Lookout"]},
    {"id":"polar_station","name":"Polar Station","emoji":"🧊","pack":"outdoor","roles":["Medic","Geologist","Expedition Leader","Biologist","Radioman","Hydrologist","Meteorologist","Cook"]},
    {"id":"police_station","name":"Police Station","emoji":"🚔","pack":"classic","roles":["Detective","Lawyer","Journalist","Criminalist","Archivist","Patrol Officer","Criminal","Witness"]},
    {"id":"restaurant","name":"Restaurant","emoji":"🍽️","pack":"classic","roles":["Musician","Customer","Bouncer","Hostess","Head Chef","Food Critic","Waiter","Bartender"]},
    {"id":"school","name":"School","emoji":"🏫","pack":"classic","roles":["Gym Teacher","Student","Principal","Security Guard","Janitor","Lunch Lady","Maintenance Man","Teacher"]},
    {"id":"service_station","name":"Service Station","emoji":"⛽","pack":"outdoor","roles":["Manager","Tire Specialist","Biker","Car Owner","Car Wash Operator","Electrician","Auto Mechanic","Cashier"]},
    {"id":"space_station","name":"Space Station","emoji":"🚀","pack":"classic","roles":["Engineer","Alien","Space Tourist","Pilot","Commander","Scientist","Doctor","Mechanic"]},
    {"id":"submarine","name":"Submarine","emoji":"🌊","pack":"classic","roles":["Cook","Commander","Sonar Technician","Electronics Technician","Sailor","Radioman","Navigator","Engineer"]},
    {"id":"supermarket","name":"Supermarket","emoji":"🛒","pack":"classic","roles":["Cashier","Butcher","Janitor","Security Guard","Food Sample Demonstrator","Shelf Stocker","Customer","Manager"]},
    {"id":"theater","name":"Theater","emoji":"🎭","pack":"classic","roles":["Coat Check Lady","Prompter","Cashier","Director","Actor","Spotlight Operator","Ticket Inspector","Stagehand"]},
    {"id":"university","name":"University","emoji":"🎓","pack":"classic","roles":["Graduate Student","Professor","Dean","Psychologist","Maintenance Man","Student","Janitor","Librarian"]},
    {"id":"zoo","name":"Zoo","emoji":"🦁","pack":"outdoor","roles":["Zookeeper","Visitor","Photographer","Child","Veterinarian","Tour Guide","Researcher","Cleaner"]},
    {"id":"ski_resort","name":"Ski Resort","emoji":"🎿","pack":"outdoor","roles":["Lift Operator","Ski Patrol","Instructor","Lost Skier","Lodge Bartender","Snowboarder","Equipment Rental Clerk","Mountain Photographer"]},
    {"id":"campsite","name":"Campsite","emoji":"🏕️","pack":"outdoor","roles":["Park Ranger","Family Camper","Solo Backpacker","Wildlife Photographer","Bored Teen","Camp Host","Tent Neighbor","Lost Tourist"]},
    {"id":"safari","name":"Safari","emoji":"🦒","pack":"outdoor","roles":["Safari Guide","Tracker","Tourist","Wildlife Photographer","Park Ranger","Poacher","Driver","Wildlife Veterinarian"]},
    {"id":"vineyard","name":"Vineyard","emoji":"🍇","pack":"outdoor","roles":["Winemaker","Sommelier","Tour Guide","Grape Picker","Cellar Master","Tasting Host","Owner","Tipsy Tourist"]},
    {"id":"lighthouse","name":"Lighthouse","emoji":"💡","pack":"outdoor","roles":["Lighthouse Keeper","Tourist","Coast Guard Officer","Boat Captain","Maintenance Worker","Historian","Storm Chaser","Seabird Watcher"]},
    {"id":"music_festival","name":"Music Festival","emoji":"🎶","pack":"outdoor","roles":["Headliner","Roadie","Security","Drunk Fan","Food Vendor","First Aid Volunteer","Sound Engineer","Lost Concertgoer"]},
    {"id":"construction_site","name":"Construction Site","emoji":"🏗️","pack":"outdoor","roles":["Foreman","Crane Operator","Carpenter","Electrician","Welder","Inspector","Lunch Truck Vendor","Apprentice"]},
    {"id":"hiking_trail","name":"Hiking Trail","emoji":"🥾","pack":"outdoor","roles":["Park Ranger","Through-Hiker","Day Hiker","Bird Watcher","Trail Runner","Trail Maintainer","Lost Tourist","Photographer"]},

    # ---- WEIRD ----
    {"id":"sleepwalker_hotel","name":"Hotel for Sleepwalkers","emoji":"🛌","pack":"weird","roles":["Front Desk Sleepwalker","Bellhop in a Trance","Dream Concierge","Insomniac Guest","Lucid Tourist","Night Manager","Sleep Doctor in the Lobby","Half-Asleep Maid"]},
    {"id":"crisis_hotline","name":"Existential Crisis Hotline","emoji":"📞","pack":"weird","roles":["Operator on Smoke Break","Caller Mid-Spiral","Trainee Reading Script","Burnout Veteran","Floor Manager","Janitor Listening In","IT Guy Under a Desk","Wrong-Number Soul"]},
    {"id":"wrong_store","name":"Department Store Where Everything Is Slightly Wrong","emoji":"🛒","pack":"weird","roles":["Cashier Who Notices","Mannequin That Just Blinked","Loudspeaker Voice","Suspicious Shopper","Manager Pretending Nothing's Off","Lost Kid","Security Guard Counting Aisles","Janitor Who's Heard Things"]},
    {"id":"villain_therapy","name":"Group Therapy for Reformed Villains","emoji":"🛋️","pack":"weird","roles":["Brave Therapist","Reformed Henchman","Nostalgic Mad Scientist","Anonymous Ex-Cult Leader","Robot Sidekick (Maintenance)","Court-Mandated Patient","Sponsor From World Domination Anonymous","Receptionist Who's Heard Every Plan"]},
    {"id":"bus_never_stops","name":"The Bus That Never Stops","emoji":"🚌","pack":"weird","roles":["Driver Who Hasn't Slept In Years","Passenger Who Boarded as a Kid","Newborn Boarder","Eternal Ticket Inspector","Stowaway in the Luggage","Onboard Snack Vendor","Mysterious Old Lady","Sleeper Who Missed Their Stop"]},
    {"id":"indoor_rain_town","name":"Town Where It Only Rains Indoors","emoji":"🌧️","pack":"weird","roles":["Indoor Umbrella Vendor","Soaked Mailman","Confused Weatherman","Mayor in Rubber Boots","Tourist Buying Towels","Out-of-Work Plumber","Houseplant Watering Service Owner","Roof Repair Skeptic"]},
    {"id":"tooth_market","name":"Tooth Fairy Black Market","emoji":"🦷","pack":"weird","roles":["Lead Buyer","Anxious First-Timer","Tooth Fairy On The Take","Inspector Sniffing Fakes","Bagman","Drill Hum Operator","Backroom Cleaner","Snitch Disguised as a Kid"]},
    {"id":"end_of_time_pizza","name":"24-Hour Pizza Place at the End of Time","emoji":"🍕","pack":"weird","roles":["Eternal Pizza Cook","Last Customer Ever","Apocalypse Tourist","Cosmic Janitor","Delivery Driver Who Took a Wrong Turn","Time-Anomaly Regular","Off-Duty Angel","Rapture Survivor"]},

    # ---- 18+ ----
    {"id":"glory_hole","name":"Glory Hole","emoji":"🕳️","pack":"adult","roles":["Curious First-Timer","Bored Regular","Bathroom Attendant","Bar Owner Looking The Other Way","Undercover Cop","Plumber (Wrong Address)","Person On The Other Side","Confused Bachelor Party Guest"]},
    {"id":"vegas_suite","name":"Vegas Hotel Suite","emoji":"🎲","pack":"adult","roles":["High Roller","Showgirl","Hotel Concierge","Hungover Best Man","Lost Newlywed","Elvis Impersonator","Pool Attendant","Confused Tourist"]},
    {"id":"speakeasy","name":"1920s Speakeasy","emoji":"🥃","pack":"adult","roles":["Bootlegger","Jazz Singer","Bartender","Flapper","Undercover Cop","Mob Boss","Cigarette Girl","Regular"]},
    {"id":"speed_dating","name":"Speed Dating Night","emoji":"💘","pack":"adult","roles":["Event Host","The Over-Sharer","The Ghoster","Server","DJ","Hopeful Romantic","Ex Who Showed Up","Lonely Cat Owner"]},
    {"id":"couples_therapy","name":"Couples Therapy Office","emoji":"💔","pack":"adult","roles":["Therapist","Partner Who Won't Talk","Partner Who Talks Too Much","Receptionist","Houseplant That Has Seen Too Much","Counselor In Training","Marriage Mediator","Supportive Friend"]},
    {"id":"drag_bar","name":"Drag Bar","emoji":"👑","pack":"adult","roles":["Headliner Queen","Bouncer","Bartender","Bachelorette","Sound Technician","Tipsy Tourist","Photographer","Backup Dancer"]},
    {"id":"dive_bar","name":"Dive Bar at 2AM","emoji":"🍺","pack":"adult","roles":["Bartender","Eight-Hour Regular","Karaoke Hero","Bouncer","Heartbroken Drinker","Pool Shark","Bachelorette Survivor","Waiting Cab Driver"]},
    {"id":"singles_cruise","name":"Singles' Cruise","emoji":"🚢","pack":"adult","roles":["Cruise Director","Tiki Bartender","Massage Therapist","Hot Tub Attendant","DJ","Lifeguard","Speed-Dating Coordinator","Senior Who Booked the Wrong Cruise"]},
    {"id":"furry_festival","name":"Furry Festival","emoji":"🦊","pack":"adult","roles":["Partial Fursuit Wearer","Very Serious Head of Security","Artist Alley Vendor","Panel Host","Photographer (Brave)","Fursuit Parade Marshal","Non-Furry Who Wandered In","Con Chair"]},
    {"id":"swingers_hotel","name":"Swingers Hotel","emoji":"🔄","pack":"adult","roles":["Front Desk Clerk Who Has Seen Everything","Enthusiastic First-Timer","Seasoned Veteran","Spouse Who Got Talked Into It","Pool Attendant","Mixologist","The One Who Chickened Out","Couples Therapist Moonlighting"]},
    {"id":"meth_lab","name":"Meth Lab","emoji":"🧪","pack":"adult","roles":["Head Chemist","Nervous Lookout","Money Launderer","Desperate Intern","Driver Who Asks No Questions","Supplier","Jumpy Investor","Health Inspector (Wrong Address)"]},
    {"id":"hell","name":"Hell","emoji":"😈","pack":"adult","roles":["Satan","Middle Management Demon","Intern Demon (First Week)","Soul Filing Yet Another Appeal","Bureaucrat Processing New Arrivals","Torturer On Lunch Break","Confused Tourist (Wrong Afterlife)","Influencer Already Making Content"]},
    {"id":"porn_set","name":"Porn Set","emoji":"🎥","pack":"adult","roles":["Director","Boom Operator (Uncomfortable)","Lead Performer","Craft Services","Continuity Person","Talent Agent","PA Running Errands","Pizza Delivery Guy (Wrong Address)"]},

    # ---- World Wonders ----
    {"id":"giza","name":"Great Pyramid of Giza","emoji":"🐫","pack":"wonders","roles":["Tourist","Camel Driver","Tour Guide","Archaeologist","Souvenir Vendor","Tomb Guard","Photographer","Bedouin"]},
    {"id":"great_wall","name":"Great Wall of China","emoji":"🏯","pack":"wonders","roles":["Tourist","Tour Guide","Watchtower Guard","Photographer","Souvenir Vendor","Park Ranger","Hiker","Historian"]},
    {"id":"machu_picchu","name":"Machu Picchu","emoji":"🦙","pack":"wonders","roles":["Tourist","Llama Wrangler","Tour Guide","Archaeologist","Park Ranger","Backpacker","Photographer","Local Porter"]},
    {"id":"colosseum","name":"Roman Colosseum","emoji":"🏟️","pack":"wonders","roles":["Tourist","Tour Guide","Gladiator Re-enactor","Souvenir Vendor","Photographer","Pickpocket","Historian","Ticket Inspector"]},
    {"id":"taj_mahal","name":"Taj Mahal","emoji":"🕌","pack":"wonders","roles":["Tourist","Tour Guide","Marble Restorer","Souvenir Vendor","Security Guard","Photographer","Honeymooner","Historian"]},
    {"id":"petra","name":"Petra","emoji":"🏺","pack":"wonders","roles":["Tourist","Bedouin Guide","Camel Driver","Archaeologist","Souvenir Vendor","Photographer","Hiker","Treasure Hunter"]},
    {"id":"stonehenge","name":"Stonehenge","emoji":"🪨","pack":"wonders","roles":["Tourist","Archaeologist","Druid","Park Ranger","Photographer","Tour Guide","Stone Mason","Historian"]},
    {"id":"christ_redeemer","name":"Christ the Redeemer","emoji":"⛰️","pack":"wonders","roles":["Tourist","Tour Guide","Photographer","Souvenir Vendor","Pilgrim","Park Ranger","Window Cleaner","Statue Restorer"]},
    {"id":"eiffel","name":"Eiffel Tower","emoji":"🗼","pack":"wonders","roles":["Tourist","Tour Guide","Elevator Operator","Photographer","Souvenir Vendor","Painter","Restaurant Waiter","Pickpocket"]},
    {"id":"chichen_itza","name":"Chichen Itza","emoji":"🐍","pack":"wonders","roles":["Tourist","Tour Guide","Archaeologist","Souvenir Vendor","Park Ranger","Photographer","Echo Tester","Historian"]},

    # ---- Rooms 609-614 ----
    {"id":"room_609","name":"Room 609","emoji":"🎉","pack":"rooms","roles":["Roommate","DJ","Drunk Friend","Awkward Stranger","Beer Pong Champion","Sober Driver","Couch Sleeper","Uninvited Guest"]},
    {"id":"room_610","name":"Room 610","emoji":"📚","pack":"rooms","roles":["Roommate","Caffeinated Student","Group Project Member","Tutor","Procrastinator","Midnight Snacker","Library Defector","Whiteboard Owner"]},
    {"id":"room_611","name":"Room 611","emoji":"🎮","pack":"rooms","roles":["Roommate","Streamer","LAN Party Guest","Energy Drink Drinker","AFK Player","Spectator","Cable Manager","Headset Hoarder"]},
    {"id":"room_612","name":"Room 612","emoji":"🧼","pack":"rooms","roles":["Roommate","OCD Cleaner","Visitor With Shoes On","Plant Parent","Candle Lighter","Linen Folder","Dust Allergic","Hand Sanitizer Pump"]},
    {"id":"room_613","name":"Room 613","emoji":"🔮","pack":"rooms","roles":["Roommate","Conspiracy Theorist","Light Avoider","Late-Night Whisperer","Door Knocker","Lurker","Pet Owner","Tarot Reader"]},
    {"id":"room_614","name":"Room 614","emoji":"🌀","pack":"rooms","roles":["Roommate","Hoarder","Dish Avoider","Alarm Snoozer","Mystery Stain Investigator","Loud Texter","Trash-Bag Procrastinator","Pizza Box Architect"]},

    # ---- Fictional ----
    {"id":"hogwarts","name":"Hogwarts","emoji":"🪄","pack":"fictional","roles":["Headmaster","Student","Professor","Ghost","House Elf","Quidditch Player","Ministry Official","Groundskeeper"]},
    {"id":"mordor","name":"Mordor","emoji":"👁️","pack":"fictional","roles":["Sauron","Orc Captain","Nazgûl","Slave","Goblin Smith","Mouth of Sauron","Watchtower Guard","Mountain Troll"]},
    {"id":"death_star","name":"Death Star","emoji":"💀","pack":"fictional","roles":["Stormtrooper","Sith Lord","Imperial Officer","Engineer","Admiral","Prisoner","TIE Pilot","Bounty Hunter"]},
    {"id":"tatooine","name":"Tatooine","emoji":"🏜️","pack":"fictional","roles":["Moisture Farmer","Jawa","Cantina Bartender","Smuggler","Bounty Hunter","Sand Person","Pod Racer","Hutt Crime Lord"]},
    {"id":"wakanda","name":"Wakanda","emoji":"🐆","pack":"fictional","roles":["King","Dora Milaje Warrior","Tribal Elder","Vibranium Miner","Border Tribe Member","Royal Scientist","Visitor","Shaman"]},
    {"id":"springfield","name":"Springfield","emoji":"🍩","pack":"fictional","roles":["Bartender","Power Plant Worker","School Bus Driver","Police Chief","Local Drunk","News Anchor","Mayor","Donut-Loving Dad"]},
    {"id":"gotham","name":"Gotham City","emoji":"🦇","pack":"fictional","roles":["Police Commissioner","Henchman","Mob Boss","Vigilante","Reporter","District Attorney","Asylum Patient","Wealthy Socialite"]},
    {"id":"westeros","name":"King's Landing","emoji":"🐉","pack":"fictional","roles":["King","Knight","Maester","Servant","Lord","Lady","Stable Boy","Bastard"]},
    {"id":"jurassic_park","name":"Jurassic Park","emoji":"🦖","pack":"fictional","roles":["Paleontologist","Park Owner","Game Warden","Tourist","Geneticist","Loose Velociraptor","Park Engineer","Tour Guide"]},
    {"id":"hawkins","name":"Hawkins, Indiana","emoji":"🌲","pack":"fictional","roles":["High Schooler","Police Officer","Worried Mom","Government Agent","Arcade Owner","Babysitter","Newspaper Editor","Lab Scientist"]},

    # ---- Rick & Morty ----
    {"id":"citadel_of_ricks","name":"Citadel of Ricks","emoji":"🌀","pack":"rick-morty","roles":["Council Rick","Cop Rick","Janitor Morty","Tax Rick","Receptionist Rick","Eyepatch Morty","Bartender Rick","Confused New Morty"]},
    {"id":"smith_garage","name":"The Smith Garage","emoji":"🔧","pack":"rick-morty","roles":["Rick Sanchez","Morty Smith","Summer Smith","Jerry Smith","Beth Smith","Mr. Meeseeks","Squanchy","Birdperson"]},
    {"id":"blips_and_chitz","name":"Blips and Chitz","emoji":"🎮","pack":"rick-morty","roles":["Roy Player Stuck for 40 Years","Arcade Attendant","Snack Bar Worker","Alien Teen","Meeseeks Champion","Cleanup Crew","Game Repair Tech","Confused First-Timer"]},
    {"id":"federation_prison","name":"Galactic Federation Prison","emoji":"👽","pack":"rick-morty","roles":["Inmate Rick","Federation Guard","Warden","Krombopulos Michael","Cellmate","Visiting Morty","Federation Bureaucrat","Snitch"]},
    {"id":"anatomy_park","name":"Anatomy Park","emoji":"🫀","pack":"rick-morty","roles":["Park Ranger","Tour Guide","Gift Shop Clerk","Disease Mascot","Visiting Tourist","Bubonic Plague","Hepatitis A","Park Maintenance"]},
    {"id":"interdim_cable","name":"Interdimensional Cable Studio","emoji":"📺","pack":"rick-morty","roles":["Personal Space Salesman","Ants in My Eyes Johnson","Two Brothers Director","Real Fake Doors Rep","Bored Channel Surfer","Studio Audience Plant","Movie Trailer Voice","Lovely Cooking Show Host"]},
    {"id":"birdperson_wedding","name":"Birdperson's Wedding","emoji":"🦅","pack":"rick-morty","roles":["Birdperson","Tammy","Rick Sanchez","Squanchy","Beth Smith","Jerry (Crashing)","Federation Spy","Wedding Officiant"]},
    {"id":"plumbus_factory","name":"Plumbus Factory","emoji":"🔩","pack":"rick-morty","roles":["Dingle-Bop Smoother","Schleem Repurposer","Hizzards Charger","Fleeb Juicer","Plumbus Inspector","Blamf Cutter","Factory Tour Guide","Machine Operator"]},
    {"id":"butt_dimension","name":"Farting Butt Dimension","emoji":"🍑","pack":"rick-morty","roles":["Tourist Rick","Confused Morty","Loud Local Butt","Soft Local Butt","Fart Sommelier","Methane Surveyor","Butt Whisperer","Newly-Risen Butt"]},
    {"id":"hamsters_in_butts","name":"Hamsters in Butts Dimension","emoji":"🐹","pack":"rick-morty","roles":["Hamster Wrangler","Local With Hamster","Black Market Dealer","Hamster Veterinarian","Tourist Rick","Empty-Butt Newcomer","Hamster Trainer","Confused Morty"]},

    # ---- T-Town ----
    {"id":"samf","name":"Studentersamfundet","emoji":"🔴","pack":"t-town","roles":["Society President","Bartender","Security Guard","Student","DJ","Event Organizer","Regular","Cleaner"]},
    {"id":"bodegaen","name":"Bodegaen","emoji":"🍺","pack":"t-town","roles":["Bartender","Regular","Bouncer","Manager","Server","Chef","Tourist","Food Critic"]},
    {"id":"dt","name":"DT","emoji":"🎤","pack":"t-town","roles":["Bartender","Bouncer","DJ","Student","Regular","Manager","Karaoke Singer","First-Timer"]},
    {"id":"nanjing_house","name":"Nanjing House","emoji":"🥢","pack":"t-town","roles":["Chef","Waiter","Customer","Manager","Delivery Driver","Dishwasher","Food Critic","Host"]},
    {"id":"sesam","name":"Sesam","emoji":"🍔","pack":"t-town","roles":["Barista","Bartender","Regular","Manager","Chef","Waitress","Food Blogger","Student"]},
    {"id":"sit_treningsenter","name":"SiT Treningsenter","emoji":"🏋️","pack":"t-town","roles":["Personal Trainer","Student","Receptionist","Janitor","Yoga Instructor","Gym Regular","Coach","New Member"]},
    {"id":"buran","name":"Buran","emoji":"🚬","pack":"t-town","roles":["Bartender","DJ","Bouncer","Regular","Manager","Student","Karaoke Singer","First-Timer"]},
    {"id":"oriental_thai","name":"Oriental Thai Massasje","emoji":"💆","pack":"t-town","roles":["Masseuse","Customer","Receptionist","Owner","Therapist","Apprentice","Booking Agent","Cleaner"]},
    {"id":"dreams_showbar","name":"Dreams Showbar","emoji":"🌙","pack":"t-town","roles":["Performer","Bartender","Bouncer","Customer","DJ","Manager","VIP Guest","Server"]},
    {"id":"kino","name":"Prinsen Kino","emoji":"🎬","pack":"t-town","roles":["Ticket Inspector","Popcorn Vendor","Projectionist","Manager","Date Night Customer","Film Critic","Usher","Cleaning Staff"]},
    {"id":"sluppen","name":"Sluppen","emoji":"🏢","pack":"t-town","roles":["Office Worker","Bus Commuter","Construction Worker","Cyclist","Shop Owner","Security Guard","Delivery Driver","Janitor"]},
    {"id":"pirbadet","name":"Pirbadet","emoji":"🏊","pack":"t-town","roles":["Lifeguard","Swimmer","Manager","Instructor","Family Visitor","Maintenance Worker","Receptionist","Water Slide Enthusiast"]},
    {"id":"me_nightclub","name":"ME Nightclub","emoji":"🌈","pack":"t-town","roles":["Drag Queen Headliner","Bartender","Bouncer","DJ","Go-Go Dancer","Regular","First-Timer","Photographer"]},
    {"id":"trondheim_torg","name":"Trondheim Torg","emoji":"🛍️","pack":"t-town","roles":["Mall Security Guard","Store Clerk","Window Shopper","Cleaner","Mall Manager","Food Court Worker","Teen Hanging Out","Lost Tourist"]},
    {"id":"bakklandet","name":"Bakklandet","emoji":"☕","pack":"t-town","roles":["Barista","Tourist With Camera","Pastry Baker","Outdoor Café Customer","Local on a Walk","Cyclist","Old House Owner","Street Photographer"]},
    {"id":"realfagsbygget","name":"Realfagsbygget","emoji":"🧪","pack":"t-town","roles":["Professor","PhD Student","Lab Technician","Bachelor Student Cramming","Janitor","Cafeteria Worker","Lost First-Year","Building Coordinator"]},

    # ---- Gløshaugen ----
    {"id":"hovedbygget","name":"Hovedbygget","emoji":"🏰","pack":"gloshaugen","roles":["Rector","Dean","Tour Guide","Tourist Taking Photos","PhD Defending Thesis","Janitor","Building Watchman","Lost First-Year"]},
    {"id":"sentralbygg","name":"Sentralbygg","emoji":"🏢","pack":"gloshaugen","roles":["Architect Lecturer","Engineering Student","Elevator Repair Tech","Janitor","Lost Visitor","Cafeteria Worker","IT Support","Stairwell Climber"]},
    {"id":"stripa","name":"Stripa","emoji":"🚶","pack":"gloshaugen","roles":["Hurried Student","Maintenance Worker","Bicycle Sneaker","Lost First-Year","Patrol Guard","Energy Drink Promoter","Coffee-Spilling Professor","Campus Tour Guide"]},
    {"id":"kjelhuset","name":"Kjelhuset","emoji":"🍽️","pack":"gloshaugen","roles":["Cafeteria Cook","Hungry Student","Cashier","Cleaner","Coffee Drinker","Group Project Member","Sit-and-Study Veteran","Burned-Out PhD Candidate"]},
    {"id":"hangaren","name":"Hangaren","emoji":"🏐","pack":"gloshaugen","roles":["Sports Instructor","Volleyball Player","Climber","Janitor","Yoga Class Leader","Locker Room Attendant","Idrettsrådet Member","Tournament Organizer"]},
    {"id":"gamle_elektro","name":"Gamle Elektro","emoji":"⚡","pack":"gloshaugen","roles":["Electrical Engineering Professor","Lab Assistant","Master's Student","Janitor","Cable Hoarder","Building Coordinator","Wandering Tourist","Equipment Borrower"]},
    {"id":"tekniskbiblioteket","name":"Tekniskbiblioteket","emoji":"📚","pack":"gloshaugen","roles":["Librarian","Quiet Studier","Group Study Whisperer","Janitor","Coffee Sneaker","Book Reservation Hunter","Wifi Mooch","Late-Night Cram Student"]},
    {"id":"hogskoleparken","name":"Høgskoleparken","emoji":"🌳","pack":"gloshaugen","roles":["Sunbathing Student","Frisbee Player","Dog Walker","Park Maintenance","Lunchbreak Faculty","Russ Reveller","Photographer","Picnic-Goer"]},

    # ---- Dark ----
    {"id":"auschwitz","name":"Auschwitz","emoji":"🚂","pack":"spicy","roles":["Prison Guard","Prisoner_101","Head of Logistics","Gasser","Janitor","Prisoner_103","True Believer","Escapee"]},
    {"id":"mayan_sacrifice","name":"Mayan Human Sacrifice Stand","emoji":"🗿","pack":"spicy","roles":["Human Being Sacrificed","Audience Member","Head of Ceremony","Executioner","Priest","Drummer","Obsidian Knife Sharpener","Visiting Noble"]},
    {"id":"hitler_bunker","name":"Hitler's Bunker (End of War)","emoji":"🎖️","pack":"spicy","roles":["Adolf Hitler","Eva Braun","Joseph Goebbels","Magda Goebbels","Goebbels Child","SS Guard","Personal Secretary","Loyal General"]},
    {"id":"cotton_farm","name":"Cotton Farm, 1850s Mississippi","emoji":"🌾","pack":"spicy","roles":["Farm Owner","Cotton Picker","Overseer","Field Hand","House Servant","Visiting Buyer","Stable Boy","Foreman"]},
    {"id":"gulag","name":"Siberian Gulag","emoji":"❄️","pack":"spicy","roles":["Camp Commandant","Political Prisoner","Common Criminal","Guard","Camp Cook","Camp Doctor","Informant","Escape Planner"]},
    {"id":"epstein_island","name":"Epstein Island","emoji":"🏝️","pack":"spicy","roles":["Jeffrey Epstein","Stephen Hawking","Bill Clinton","19 yr old Model","Janitor","Undercover Journalist","Private Pilot","Personal Chef"]},
    {"id":"gaza_strip","name":"Gaza Strip","emoji":"🕊️","pack":"spicy","roles":["Foreign Journalist","UN Aid Worker","Local Civilian","Hamas Fighter","IDF Soldier","Doctor Without Borders","Tunnel Digger","Foreign Diplomat"]},
    {"id":"crack_lair","name":"Baltimore Crack Lair","emoji":"💉","pack":"spicy","roles":["Tweaker Getting High","Cynical Drug Dealer","Lookout","Money Counter","Strung-Out Regular","Undercover Cop","Supplier","Desperate New Customer"]},
    {"id":"prison_shower","name":"Prison Shower","emoji":"🚿","pack":"spicy","roles":["Newcomer","Gang Leader","Snitch","Lifer","Guard","Trustee","Old-Timer","Shower Lookout"]},
    {"id":"mental_hospital","name":"Experimental Unit, 1950s Mental Hospital","emoji":"🧠","pack":"spicy","roles":["Lobotomy Patient","Head Doctor","Skeptical Nurse","Test Subject","Orderly","Visiting Researcher","Janitor","Patient Who Knows Too Much"]},
]


MIME = {
    ".html": "text/html; charset=utf-8",
    ".js":   "application/javascript",
    ".css":  "text/css",
    ".svg":  "image/svg+xml",
    ".png":  "image/png",
    ".ico":  "image/x-icon",
    ".json": "application/json",
}

CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no I, O, 0, 1
rooms: dict[str, dict] = {}


# ---------- helpers ----------
def make_code() -> str:
    while True:
        c = "".join(random.choices(CODE_CHARS, k=4))
        if c not in rooms:
            return c

def uid() -> str:
    return secrets.token_hex(8)

def sanitize_name(s) -> str:
    s = str(s or "").strip()
    s = "".join(ch for ch in s if ch.isprintable())
    return s[:20]

def public_player(p):
    return {"id": p["id"], "name": p["name"], "connected": p["connected"]}

def public_loc(l):
    return {"id": l["id"], "name": l["name"], "pack": l["pack"], "emoji": l.get("emoji", "")}

async def ws_send(ws, obj):
    if ws is None:
        return
    try:
        await ws.send(json.dumps(obj))
    except Exception:
        pass

async def broadcast_room(room):
    payload = json.dumps({
        "t": "roomState",
        "code": room["code"],
        "hostId": room["hostId"],
        "players": [public_player(p) for p in room["players"]],
        "state": room["state"],
        "settings": room["settings"],
    })
    for p in room["players"]:
        if p["ws"] is not None:
            try:
                await p["ws"].send(payload)
            except Exception:
                pass

def find_by_ws(ws):
    for room in rooms.values():
        for p in room["players"]:
            if p["ws"] is ws:
                return room, p
    return None, None

def find_by_session(sid):
    for room in rooms.values():
        for p in room["players"]:
            if p.get("sessionId") == sid:
                return room, p
    return None, None


# ---------- game logic ----------
async def start_round(room, duration_sec, pack_id):
    pool = LOCATIONS if pack_id == "all" else [l for l in LOCATIONS if l["pack"] == pack_id]
    if not pool:
        pool = LOCATIONS
    location = random.choice(pool)
    n = len(room["players"])
    if n < 2:
        return
    spy_idx = random.randrange(n)
    role_pool = location["roles"][:]
    random.shuffle(role_pool)
    roles = {}
    r = 0
    for i, p in enumerate(room["players"]):
        if i == spy_idx:
            continue
        roles[p["id"]] = role_pool[r % len(role_pool)] if role_pool else "Player"
        r += 1
    first_asker = random.choice(room["players"])
    ends_at_ms = int((time.time() + duration_sec) * 1000)
    room["state"] = "inRound"
    room["round"] = {
        "location": location,
        "spyId": room["players"][spy_idx]["id"],
        "roles": roles,
        "firstAskerId": first_asker["id"],
        "firstAskerName": first_asker["name"],
        "endsAt": ends_at_ms,
        "durationSec": duration_sec,
        "pack": pack_id,
        "paused": False,
        "remainingMs": None,
    }
    all_locs = [public_loc(l) for l in pool]
    spy_id = room["round"]["spyId"]
    for p in room["players"]:
        is_spy = p["id"] == spy_id
        await ws_send(p["ws"], {
            "t": "roundStarted",
            "isSpy": is_spy,
            "location": None if is_spy else {"id": location["id"], "name": location["name"], "emoji": location.get("emoji", "")},
            "role": None if is_spy else roles[p["id"]],
            "firstAskerName": first_asker["name"],
            "remainingMs": int(duration_sec * 1000),
            "durationSec": duration_sec,
            "allLocations": all_locs,
            "paused": False,
        })
    if room.get("roundTask"):
        room["roundTask"].cancel()
        room["roundTask"] = None
    await broadcast_room(room)

async def end_round(room, reason):
    if room["state"] != "inRound":
        return
    if room.get("roundTask"):
        room["roundTask"].cancel()
        room["roundTask"] = None
    r = room.get("round")
    if not r:
        return
    reveal = {
        "t": "roundEnded",
        "reason": reason,
        "spyId": r["spyId"],
        "location": {"id": r["location"]["id"], "name": r["location"]["name"]},
        "roles": r["roles"],
    }
    room["state"] = "roundEnded"
    for p in room["players"]:
        await ws_send(p["ws"], reveal)
    await broadcast_room(room)


# ---------- message handlers ----------
async def handle_create(ws, msg):
    name = sanitize_name(msg.get("name"))
    if not name:
        await ws_send(ws, {"t": "error", "msg": "Name required"})
        return
    code = make_code()
    pid, sid = uid(), uid()
    player = {"id": pid, "sessionId": sid, "name": name, "ws": ws, "connected": True}
    room = {
        "code": code, "players": [player], "hostId": pid,
        "state": "lobby", "round": None, "roundTask": None,
        "settings": {"durationSec": 480, "pack": "all"},
    }
    rooms[code] = room
    await ws_send(ws, {"t": "joined", "you": pid, "sessionId": sid, "code": code})
    await broadcast_room(room)

async def handle_join(ws, msg):
    code = str(msg.get("code", "")).upper().strip()
    name = sanitize_name(msg.get("name"))
    sid = msg.get("sessionId")

    # Reconnect path
    if sid:
        rr, pp = find_by_session(sid)
        if rr and rr["code"] == code:
            pp["ws"] = ws
            pp["connected"] = True
            await ws_send(ws, {"t": "joined", "you": pp["id"], "sessionId": sid, "code": code})
            if rr["state"] == "inRound" and rr.get("round"):
                rd = rr["round"]
                is_spy = pp["id"] == rd["spyId"]
                await ws_send(ws, {
                    "t": "roundStarted",
                    "isSpy": is_spy,
                    "location": None if is_spy else {"id": rd["location"]["id"], "name": rd["location"]["name"], "emoji": rd["location"].get("emoji", "")},
                    "role": None if is_spy else rd["roles"].get(pp["id"]),
                    "firstAskerName": rd["firstAskerName"],
                    "remainingMs": (rd.get("remainingMs") if rd.get("paused") else max(0, rd["endsAt"] - int(time.time() * 1000))),
                    "durationSec": rd["durationSec"],
                    "allLocations": [public_loc(l) for l in (LOCATIONS if rd.get("pack","all") == "all" else [x for x in LOCATIONS if x["pack"] == rd.get("pack")])],
                    "paused": rd.get("paused", False),
                })
            elif rr["state"] == "roundEnded" and rr.get("round"):
                rd = rr["round"]
                await ws_send(ws, {
                    "t": "roundEnded", "reason": "reconnect", "spyId": rd["spyId"],
                    "location": {"id": rd["location"]["id"], "name": rd["location"]["name"]},
                    "roles": rd["roles"],
                })
            await broadcast_room(rr)
            return

    room = rooms.get(code)
    if not room:
        await ws_send(ws, {"t": "error", "msg": "Room not found"})
        return
    if not name:
        await ws_send(ws, {"t": "error", "msg": "Name required"})
        return
    if room["state"] == "inRound":
        await ws_send(ws, {"t": "error", "msg": "Round already in progress"})
        return
    if any(p["name"].lower() == name.lower() for p in room["players"]):
        await ws_send(ws, {"t": "error", "msg": "Name taken in this room"})
        return
    pid, new_sid = uid(), uid()
    player = {"id": pid, "sessionId": new_sid, "name": name, "ws": ws, "connected": True}
    room["players"].append(player)
    await ws_send(ws, {"t": "joined", "you": pid, "sessionId": new_sid, "code": code})
    await broadcast_room(room)

async def handle_message(ws, msg):
    t = msg.get("t")
    if t == "create":
        await handle_create(ws, msg); return
    if t == "join":
        await handle_join(ws, msg); return

    room, player = find_by_ws(ws)
    if not room or not player:
        return

    if t == "settings":
        if player["id"] != room["hostId"]: return
        s = room["settings"]
        try:
            d = int(msg.get("durationSec", s["durationSec"]))
            s["durationSec"] = max(60, min(900, d))
        except (TypeError, ValueError):
            pass
        if "pack" in msg:
            p = str(msg["pack"])
            if p in ("all", "classic", "outdoor", "weird", "adult", "spicy", "t-town", "fictional", "rooms", "wonders", "rick-morty", "gloshaugen"):
                s["pack"] = p
        await broadcast_room(room)

    elif t == "startRound":
        if player["id"] != room["hostId"]: return
        if room["state"] == "inRound": return
        connected = [p for p in room["players"] if p["connected"]]
        if len(connected) < 2:
            await ws_send(ws, {"t": "error", "msg": "Need at least 2 connected players"})
            return
        s = room["settings"]
        await start_round(room, s["durationSec"], s["pack"])

    elif t == "endRound":
        if player["id"] != room["hostId"]: return
        await end_round(room, "manual")

    elif t == "pauseRound":
        if player["id"] != room["hostId"]: return
        if room["state"] != "inRound": return
        rd = room.get("round")
        if not rd or rd.get("paused"): return
        remaining = max(0, rd["endsAt"] - int(time.time() * 1000))
        rd["paused"] = True
        rd["remainingMs"] = remaining
        if room.get("roundTask"):
            room["roundTask"].cancel()
            room["roundTask"] = None
        for p in room["players"]:
            await ws_send(p["ws"], {"t": "roundPaused", "remainingMs": remaining})

    elif t == "resumeRound":
        if player["id"] != room["hostId"]: return
        if room["state"] != "inRound": return
        rd = room.get("round")
        if not rd or not rd.get("paused"): return
        remaining_ms = rd.get("remainingMs") or 0
        new_ends_at = int(time.time() * 1000) + remaining_ms
        rd["endsAt"] = new_ends_at
        rd["paused"] = False
        rd["remainingMs"] = None
        for p in room["players"]:
            await ws_send(p["ws"], {"t": "roundResumed", "remainingMs": remaining_ms})

    elif t == "playAgain":
        if player["id"] != room["hostId"]: return
        room["state"] = "lobby"
        room["round"] = None
        await broadcast_room(room)

    elif t == "kick":
        if player["id"] != room["hostId"]: return
        if room["state"] == "inRound": return
        target = next((p for p in room["players"] if p["id"] == msg.get("playerId")), None)
        if target and target["id"] != room["hostId"]:
            try:
                if target["ws"] is not None:
                    await ws_send(target["ws"], {"t": "kicked"})
                    await target["ws"].close()
            except Exception:
                pass
            room["players"] = [p for p in room["players"] if p["id"] != target["id"]]
            await broadcast_room(room)

    elif t == "leave":
        room["players"] = [p for p in room["players"] if p["id"] != player["id"]]
        if not room["players"]:
            rooms.pop(room["code"], None)
            if room.get("roundTask"):
                room["roundTask"].cancel()
            return
        if player["id"] == room["hostId"]:
            room["hostId"] = room["players"][0]["id"]
        await broadcast_room(room)


async def handle_disconnect(ws):
    room, player = find_by_ws(ws)
    if not room or not player:
        return
    player["connected"] = False
    player["ws"] = None
    await broadcast_room(room)

    code = room["code"]
    pid = player["id"]

    async def cleanup():
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            return
        r = rooms.get(code)
        if not r:
            return
        p = next((pp for pp in r["players"] if pp["id"] == pid), None)
        if not p or p["connected"]:
            return
        if r["state"] == "lobby":
            r["players"] = [pp for pp in r["players"] if pp["id"] != pid]
        if r["hostId"] == pid:
            new_host = next((pp for pp in r["players"] if pp["connected"]), None)
            if new_host:
                r["hostId"] = new_host["id"]
        if not any(pp["connected"] for pp in r["players"]):
            rooms.pop(code, None)
            if r.get("roundTask"):
                r["roundTask"].cancel()
            return
        await broadcast_room(r)

    asyncio.create_task(cleanup())


# ---------- ws + http ----------
async def ws_handler(ws):
    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
            if not isinstance(msg, dict):
                continue
            try:
                await handle_message(ws, msg)
            except Exception as e:
                print(f"handler error: {e}")
    finally:
        await handle_disconnect(ws)


def serve_static(path: str) -> Response:
    if path in ("", "/"):
        path = "/index.html"
    rel = path.split("?", 1)[0].split("#", 1)[0].lstrip("/")
    target = (PUBLIC / rel).resolve()
    try:
        target.relative_to(PUBLIC)
    except ValueError:
        body = b"Forbidden\n"
        return Response(HTTPStatus.FORBIDDEN, "Forbidden",
                        Headers([("Content-Type","text/plain"),("Content-Length",str(len(body)))]),
                        body)
    if not target.is_file():
        body = b"Not Found\n"
        return Response(HTTPStatus.NOT_FOUND, "Not Found",
                        Headers([("Content-Type","text/plain"),("Content-Length",str(len(body)))]),
                        body)
    body = target.read_bytes()
    headers = Headers([
        ("Content-Type", MIME.get(target.suffix.lower(), "application/octet-stream")),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
    ])
    return Response(HTTPStatus.OK, "OK", headers, body)


def process_request(connection, request):
    upgrade = request.headers.get("Upgrade", "") or ""
    if upgrade.lower() == "websocket":
        return None
    if request.path.split("?", 1)[0] == "/locations.json":
        body = json.dumps(LOCATIONS, ensure_ascii=False).encode("utf-8")
        return Response(HTTPStatus.OK, "OK",
                        Headers([
                            ("Content-Type", "application/json; charset=utf-8"),
                            ("Content-Length", str(len(body))),
                            ("Cache-Control", "no-store"),
                        ]),
                        body)
    return serve_static(request.path)


def lan_ip() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return None


async def main():
    print("Spyfall is running.")
    print(f"  Local:    http://localhost:{PORT}")
    ip = lan_ip()
    if ip:
        print(f"  LAN:      http://{ip}:{PORT}   (share this with players on the same wifi)")
    print("Press Ctrl+C to stop.")
    async with serve(ws_handler, "0.0.0.0", PORT, process_request=process_request):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
