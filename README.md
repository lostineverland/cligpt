# CLIGPT

A simple python script to interact with OpenAI's API. The script is an executable Python file built on the standard library (no dependencies). Context is maintained per session, where a session is any invocation of the script. Thus if you want a new session, simply run it again. 

Every interaction is logged at the current working directory in a folder called `GPT_logs`. These will be written as Markdown files and organized by `year/month/` based on the timestamp of execution.

## Installation

- clone the repository, ensure that `cligpt.py` is executable
- add to your `PATH` and run it
  - `cligpy`
  - I tend to create a symlink to the executable
    -  `cd ~/bin && ln -s <repository>/cligpt.py cligpt`
  - this creates the config file
- Obtain an API key from [OpenAI](https://platform.openai.com/api-keys)
- place the key in `$HOME/.cligpt`
  - replace the value `sk-################################################` with your key
  - this file include other default values

## Use

Because the prompt allows for multiline entries, it takes an empty line to signal that you're done. When the entry has been accepted it will print `...`, which only happens after hitting return on an empty line. The query is then sent to openAI and the results are both returned to the terminal and written to the log file. Depending on the model used, it can take a long time to get a response (> 1 minute).

To exit, just send an empty query (hit enter on an empty query).

```sh
➜  ~ cligpt -m gpt-4-turbo-preview "You are a travel agent"
args: Namespace(role='You are a travel agent', model='gpt-4-turbo-preview')
gpt-4-turbo-preview:
I'm looking for a vacation with beach and mountains.

...

Answer:
-------
Certainly! Combining beach relaxation with mountain adventures in a single trip can offer you the best of both worlds. Here are a few destinations that beautifully blend sandy shores with majestic mountains, providing an array of activities and breathtaking scenery:

1. **Cape Town, South Africa** - Cape Town is a stunning choice, offering beautiful beaches such as Camps Bay and Clifton Beach, with the iconic Table Mountain as its backdrop. You can enjoy the vibrant city life, hike or take a cable car up Table Mountain, and even explore the Cape Winelands, which are a short drive away.

2. **Maui, Hawaii, USA** - Maui is famous for its diverse landscapes. You can relax on the beautiful beaches of Kaanapali or Wailea, drive the scenic Road to Hana to explore the lush mountainsides, or hike in the Haleakalā National Park, which offers an astonishing volcanic crater at its summit.

3. **Queenstown, New Zealand** - Known as the adventure capital of the world, Queenstown is perfect for those who crave adventure amidst natural beauty. It's nestled on the shores of Lake Wakatipu, with the Remarkables mountain range providing a stunning backdrop. You can enjoy bungee jumping, skydiving, and a multitude of water activities on the lake.

4. **Amalfi Coast, Italy** - The Amalfi Coast offers picturesque cliffs adorned with colorful villages overlooking the Tyrrhenian Sea. Enjoy the beautiful beaches, hike the Path of the Gods for spectacular views, and savor the delicious Italian cuisine and limoncello.

5. **Kauai, Hawaii, USA** - Kauai, also known as the Garden Isle, features dramatic mountains and pristine beaches. The Na Pali Coast offers some of the most breathtaking hiking trails and coastline views, while beaches like Poipu Beach are perfect for relaxation and snorkeling.

6. **Lofoten Islands, Norway** - For a more unique and off-the-beaten-path experience, the Lofoten Islands offer stunning Arctic beaches and rugged mountain landscapes. You can enjoy midnight sun in the summer or the Northern Lights in the winter, alongside activities like hiking, fishing, and kayaking.

Each of these destinations offers a rich blend of beach relaxation and mountain adventures, along with unique cultural experiences. Depending on your preferences for climate, travel distance, and specific interests, any of these locations could provide an unforgettable vacation. When planning, consider the time of year and local weather patterns to make the most of your trip.



gpt-4-0125-preview:

```
