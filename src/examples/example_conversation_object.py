from datetime import datetime
from src.model.conversation_dataclasses import Conversation, Branch, Message, Response

conversation = Conversation(
    id="conv_123",
    title="Sample Conversation",
    branches=[
        Branch(
            id=0,
            parent_branch_id=None,
            parent_message_id=None,
            messages=[
                Message(
                    id=0,
                    user_id="user1",
                    text="Hello, how are you?",
                    timestamp=datetime(2023, 6, 1, 10, 0, 0),
                    response=Response(
                        id="resp_0",
                        model="Claude 3 Opus",
                        text="I'm doing well, thank you! How can I assist you today?",
                        timestamp=datetime(2023, 6, 1, 10, 1, 0),
                    ),
                ),
                Message(
                    id=1,
                    user_id="user1",
                    text="Can you tell me about the weather forecast for tomorrow?",
                    timestamp=datetime(2023, 6, 1, 10, 2, 0),
                    response=Response(
                        id="resp_1",
                        model="Claude 3 Opus",
                        text="Sure, the weather forecast for tomorrow is sunny with a high of 75°F (24°C) and a low of 60°F (16°C). It should be a pleasant day!",
                        timestamp=datetime(2023, 6, 1, 10, 3, 0),
                    ),
                ),
                Message(
                    id=2,
                    user_id="user1",
                    text="That sounds great! Do you have any recommendations for outdoor activities?",
                    timestamp=datetime(2023, 6, 1, 10, 4, 0),
                    response=Response(
                        id="resp_2",
                        model="Claude 3 Opus",
                        text="With the nice weather, I recommend going for a hike, having a picnic in the park, or visiting a nearby beach or lake. It's a great opportunity to enjoy some outdoor time!",
                        timestamp=datetime(2023, 6, 1, 10, 5, 0),
                    ),
                ),
                Message(
                    id=3,
                    user_id="user1",
                    text="Thanks for the suggestions! I think I'll plan a picnic with friends.",
                    timestamp=datetime(2023, 6, 1, 10, 6, 0),
                    response=Response(
                        id="resp_3",
                        model="Claude 3 Opus",
                        text="That sounds like a wonderful idea! I hope you and your friends have a great time at the picnic. Enjoy the lovely weather!",
                        timestamp=datetime(2023, 6, 1, 10, 7, 0),
                    ),
                ),
                Message(
                    id=4,
                    user_id="user1",
                    text="Thank you! I'm looking forward to it.",
                    timestamp=datetime(2023, 6, 1, 10, 8, 0),
                    response=Response(
                        id="resp_4",
                        model="Claude 3 Opus",
                        text="You're welcome! If you need any other assistance, feel free to ask. Have a fantastic day!",
                        timestamp=datetime(2023, 6, 1, 10, 9, 0),
                    ),
                ),
            ],
        ),
        Branch(
            id=1,
            parent_branch_id=0,
            parent_message_id=2,
            messages=[
                Message(
                    id=5,
                    user_id="user1",
                    text="Actually, I think I might prefer to go for a hike instead. Any recommendations for good hiking trails?",
                    timestamp=datetime(2023, 6, 1, 10, 10, 0),
                    response=Response(
                        id="resp_5",
                        model="Claude 3 Opus",
                        text="Absolutely! Some popular hiking trails in the area include the Sunset Trail, the Waterfall Trail, and the Mountain View Trail. All of these offer beautiful scenery and varying levels of difficulty. Make sure to wear comfortable shoes and bring plenty of water!",
                        timestamp=datetime(2023, 6, 1, 10, 11, 0),
                    ),
                ),
                Message(
                    id=6,
                    user_id="user1",
                    text="The Waterfall Trail sounds interesting. How long is the hike?",
                    timestamp=datetime(2023, 6, 1, 10, 12, 0),
                    response=Response(
                        id="resp_6",
                        model="Claude 3 Opus",
                        text="The Waterfall Trail is a moderate hike that takes about 2-3 hours to complete, depending on your pace. It's a 4-mile round trip with an elevation gain of around 500 feet. The highlight of the trail is the stunning waterfall at the halfway point, which is a great spot to take a break and enjoy the view.",
                        timestamp=datetime(2023, 6, 1, 10, 13, 0),
                    ),
                ),
                Message(
                    id=7,
                    user_id="user1",
                    text="That sounds perfect! I'll definitely check out the Waterfall Trail. Thanks for the information!",
                    timestamp=datetime(2023, 6, 1, 10, 14, 0),
                    response=Response(
                        id="resp_7",
                        model="Claude 3 Opus",
                        text="You're welcome! I hope you enjoy the Waterfall Trail. Remember to stay safe, follow the trail markers, and leave no trace. If you have any other questions, feel free to ask!",
                        timestamp=datetime(2023, 6, 1, 10, 15, 0),
                    ),
                ),
                Message(
                    id=8,
                    user_id="user1",
                    text="Will do! I appreciate your help. Have a great day!",
                    timestamp=datetime(2023, 6, 1, 10, 16, 0),
                    response=Response(
                        id="resp_8",
                        model="Claude 3 Opus",
                        text="Thank you, you too! Enjoy your hike and take care!",
                        timestamp=datetime(2023, 6, 1, 10, 17, 0),
                    ),
                ),
                Message(
                    id=9,
                    user_id="user1",
                    text="Thanks! Bye for now.",
                    timestamp=datetime(2023, 6, 1, 10, 18, 0),
                ),
            ],
        ),
        Branch(
            id=2,
            parent_branch_id=1,
            parent_message_id=7,
            messages=[
                Message(
                    id=10,
                    user_id="user1",
                    text="One more thing, are there any recommended items I should bring on the hike?",
                    timestamp=datetime(2023, 6, 1, 10, 19, 0),
                    response=Response(
                        id="resp_10",
                        model="Claude 3 Opus",
                        text="Great question! In addition to comfortable shoes and plenty of water, I recommend bringing a backpack with a few essential items. These include sunscreen, a hat, sunglasses, snacks, a light jacket or rain gear (depending on the weather forecast), and a first-aid kit. It's also a good idea to bring a map or download an offline trail map on your phone, just in case.",
                        timestamp=datetime(2023, 6, 1, 10, 20, 0),
                    ),
                ),
                Message(
                    id=11,
                    user_id="user1",
                    text="Thanks for the tips! I'll make sure to pack those items.",
                    timestamp=datetime(2023, 6, 1, 10, 21, 0),
                    response=Response(
                        id="resp_11",
                        model="Claude 3 Opus",
                        text="You're welcome! It's always better to be prepared. Also, don't forget to charge your phone before you go and let someone know your hiking plans, just as a safety precaution. Enjoy your hike and take plenty of pictures of the beautiful waterfall!",
                        timestamp=datetime(2023, 6, 1, 10, 22, 0),
                    ),
                ),
                Message(
                    id=12,
                    user_id="user1",
                    text="That's a good point about letting someone know my plans. I'll be sure to do that. And I'll definitely take lots of photos!",
                    timestamp=datetime(2023, 6, 1, 10, 23, 0),
                    response=Response(
                        id="resp_12",
                        model="Claude 3 Opus",
                        text="Fantastic! It sounds like you're well-prepared for your hiking adventure. If you have any other questions or need further assistance, don't hesitate to reach out. Have a wonderful time on the Waterfall Trail!",
                        timestamp=datetime(2023, 6, 1, 10, 24, 0),
                    ),
                ),
                Message(
                    id=13,
                    user_id="user1",
                    text="Thank you so much for all your help! I feel confident and excited about the hike now. Take care!",
                    timestamp=datetime(2023, 6, 1, 10, 25, 0),
                    response=Response(
                        id="resp_13",
                        model="Claude 3 Opus",
                        text="You're most welcome! It's my pleasure to help. I'm thrilled that you feel confident and excited about your hiking trip. Remember, safety first and have a fantastic time! Take care and enjoy the great outdoors!",
                        timestamp=datetime(2023, 6, 1, 10, 26, 0),
                    ),
                ),
                Message(
                    id=14,
                    user_id="user1",
                    text="Will do! Thanks again. Bye!",
                    timestamp=datetime(2023, 6, 1, 10, 27, 0),
                ),
            ],
        ),
    ],
)
