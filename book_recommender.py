import requests
import os
from voice_input import get_input

youtube_api_key = os.getenv('YT_IFYKYK')

def handle_book_recommendation(user_name, memory_logger):
    print("\n=== 📚 Book Recommendation and Storytelling Experience ===")

    topic = get_input("Enter a topic or genre (e.g., fantasy, science, adventure, romance, comedy, action, psychological horror): ")
    memory_logger.log_interaction("Book Topic", topic)

    if youtube_api_key:
        book_and_storytelling_experience(youtube_api_key)
    else:
        print("❌ YouTube API key not found.")
        memory_logger.log_interaction("Book Recommendation", "YouTube API key missing")

        # ============= Book + Storytelling User Experience ==============
# --- Book Lookup ---
def get_book_from_openlibrary(query="science fiction"):
    """
    Fetches a book from Open Library based on the given query.
    """
    base_url = "https://openlibrary.org"
    search_url = f"{base_url}/search.json?q={query}&language=eng&has_fulltext=true"

    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data["docs"]:
            return f"📚 Sorry, I couldn't find any books for '{query}'. Try another topic?"

        book = data["docs"][0]
        title = book.get("title", "Unknown Title")
        author = book.get("author_name", ["Unknown Author"])[0]
        ol_id = book.get("key", "")
        book_url = f"{base_url}{ol_id}"

        return f"📘 **{title}** by {author}\n🔗 Read or borrow here: {book_url}"

    except requests.exceptions.RequestException as e:
        return f"⚠️ Error: Couldn't connect to Open Library. Details: {str(e)}"


def get_video_lists():
    """
    Returns the dictionary of video lists by genre.
    """
    return {
        "fantasy": [
            ("Chronicles of Narnia", "https://www.youtube.com/watch?v=smx1sn_BfaA"),
            ("The Hobbit", "https://www.youtube.com/watch?v=fFU3_vohIOs"),
            ("Harry Potter", "https://www.youtube.com/watch?v=FsByOCWSkvM"),
            ("The Lord of the Rings", "https://www.youtube.com/watch?v=V75dMMIW2B4"),
            ("Miss Peregrine's Home for Peculiar Children", "https://www.youtube.com/watch?v=2rhnt5rWgOM"),
            ("Forsaken Prince: Kilenya Chronicles Book One",
             "https://www.youtube.com/watch?v=gYohVoi_m_A&list=PL6kepgWUZXmp-el3a0z0IoqDhUDn4kyUg"),
            ("Ember Gods: Kilenya Chronicles Book Two", "https://www.youtube.com/watch?v=OrQugg3zYAI"),
            ("The Eyes of the Dragon by Stephen King", "https://www.youtube.com/watch?v=ycxRUnmG5ZE"),
        ],
        "science": [
            ("A Voyage to Arcturus by David Lindsay", "https://www.youtube.com/watch?v=90hLehiXM8g"),
            ("Supermind by Laurence M. Janifer & Randall Garrett", "https://www.youtube.com/watch?v=20of1yvGh5Y"),
            ("The Last Question", "https://www.youtube.com/watch?v=h4M3nL_Vb9w"),
            ("Pacific Rim by Travis Beacham", "https://www.youtube.com/watch?v=0IxQ4KLmcA0"),
            ("Hyperion by Dan Simmons", "https://www.youtube.com/watch?v=0uEBG98-bcY"),
            ("Worlds Within by Rog Phillips", "https://www.youtube.com/watch?v=NZKWTDEzRL4"),
            ("The Alchemy of Happiness by Al-Ghazali", "https://www.youtube.com/watch?v=0Ox_XcrBO0c"),
        ],
        "adventure": [
            ("The maze runner by Robert Daschner",
             "https://www.youtube.com/watch?v=sKJ1ktsVq-k&list=PLq5SGWgwX4FZt88QFxL_IDtvJd46Mtwgy"),
            ("The Dark Tower: The Gunslinger by Stephen King", "https://www.youtube.com/watch?v=ybvVLVaGiUM"),
            ("The Dark Tower: The Drawing of the Three by Stephen King", "https://www.youtube.com/watch?v=CWt5DFbGSyI"),
            ("The Dark Tower: The Waste Lands by Stephen King", "https://www.youtube.com/watch?v=vl8UK2wwBg0"),
            ("The Dark Tower: Wizard and Glass by Stephen King", "https://www.youtube.com/watch?v=Dy6kqY45csc"),
            ("The Dark Tower: The Dark Tower by Stephen King", "https://www.youtube.com/watch?v=cIkq1dKqfL0"),
        ],
        "romance": [
            ("Falling for the Movie Star by Jean Oram", "https://www.youtube.com/watch?v=rvUqJWb6FJs"),
            ("Gone With The Wind by Margaret Mitchell", "https://www.youtube.com/watch?v=pI__6gL21Co"),
            ("To all the boys I have loved before by Jenny Han ",
             "https://www.youtube.com/watch?v=Ac_fbiCvWDk, or https://www.youtube.com/watch?v=qdEcvQ5P0g4"),
            ("Pride and Prejudice by Jane Austen", "https://www.youtube.com/watch?v=eVHu5-n69qQ"),
            ("Outlander by Diana Gabaldon", "https://www.youtube.com/watch?v=cY-L5pqCCrU"),
            ("A Walk to Remember by Nicholas Sparks", "https://www.youtube.com/watch?v=ekX1c-y6xJQ"),
            ("The Fault in Our Stars by John Green", "https://www.youtube.com/watch?v=ht94ebGbScs"),
            ("The Time Traveler’s Wife by Audrey Niffenegger", "https://www.youtube.com/watch?v=uZNRMHAWl9w"),
        ],
        "comedy": [
            ("under the dome by Stephen King", "https://www.youtube.com/watch?v=UvYyzTQVy4w"),
            ("Oliver twist by Charles Dickens", "https://www.youtube.com/watch?v=cUVyaRJhKwc"),
            ("UNCLE toms Cabin by Harriet Beecher Stowe", "https://www.youtube.com/watch?v=hJUr-vS29dU"),
            ("Good Omens by Neil Gaiman & Terry Pratchett", "https://www.youtube.com/watch?v=h2GPXnANyGk"),
            ("The Hitchhiker's Guide to the Galaxy by Douglas Adams", "https://www.youtube.com/watch?v=33WOUNcAas4"),
            ("Bossypants by Tina Fey", "https://www.youtube.com/watch?v=Gzs5-C9Hu14"),
            ("Yes Please by Amy Poehler", "https://www.youtube.com/watch?v=IqVcHwKhr1Y"),
        ],
    }


def get_book_and_story_video(topic, max_videos=5):
    """
    Returns a book recommendation and up to `max_videos` related videos for the genre.
    """
    book_info = get_book_from_openlibrary(topic.lower())
    video_lists = get_video_lists()
    video_list = [item for item in video_lists.get(topic.lower(), []) if item[0] and item[1]]
    return book_info, video_list[:max_videos]


def run_video_loop(video_list):
    """
    Iterates through the video list, letting the user move through or exit.
    """
    print("\n🎥 Storytelling Videos:\n")
    current = 0
    while current < len(video_list):
        title, link = video_list[current]
        print(f"🎬 Video {current + 1} of {len(video_list)}: {title}\n🔗 Watch here: {link}\n")
        next_step = input("Type 'next' to continue or 'exit' to stop: ").strip().lower()
        if next_step != "next":
            print("👋 Exiting video loop.")
            break
        current += 1
    if current >= len(video_list):
        print("🎉 Congratulations you've reached the end of the video list!")


def book_and_storytelling_experience():
    """
    Interactive CLI with voice input for choosing a book, video, or both based on a genre.
    """
    print("\nChoose your literary journey:")
    print("1. Discover a great book 📖")
    print("2. Watch audiobooks or storytelling videos 🎧")
    print("3. Get both reading & video experiences 💡")

    choice = get_input("Say 1, 2, or 3: ")

    if choice not in {"1", "2", "3"}:
        print("❌ Invalid option. Please say 1, 2, or 3.")
        return

    topic = get_input("Say a genre like fantasy, science, romance, adventure, or comedy: ")
    book_info, video_list = get_book_and_story_video(topic)

    if choice == "1":
        print(f"\n📚 Book Recommendation:\n{book_info}")

    elif choice == "2":
        if video_list:
            run_video_loop(video_list)
        else:
            print(f"😕 Sorry, no videos found for genre '{topic}'.")

    elif choice == "3":
        print(f"\n📚 Book Recommendation:\n{book_info}")
        if video_list:
            run_video_loop(video_list)
        else:
            print(f"😕 Sorry, no videos found for genre '{topic}'.")