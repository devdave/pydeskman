
class MPlayerLogic {
    constructor(switchboard, channel) {
        this.switchboard = switchboard;
        this.channel = channel;
        console.log("MPlayer constructed");

        this.song_length = null;

        // player elements
        this.position_elm = null;

    }



    setup(document, window) {
        this.position_elm = document.getElementById("position");
        this.title_elm = document.querySelector("#player_body .title");
        this.artist_elm = document.querySelector("#player_body .artist");
        this.length_elm = document.querySelector("#player_body .length");
        this.current_time_elm = document.getElementsByClassName('current_time')[0];

        document.getElementById("open_song").addEventListener("click", evt => this.switchboard.request_load_dlg().then(this.on_file_load.bind(this)));

        this.switchboard.newSong.connect(this.on_new_song.bind(this));
        this.switchboard.songUpdate.connect(this.on_song_update.bind(this));

        console.log("MPlayer setup");

        this.switchboard.currentSong().then(this.on_check_current_song.bind(this));

        document.getElementById("play").addEventListener("click", evt => this.switchboard.play());
        document.getElementById("pause").addEventListener("click", evt => this.switchboard.pause());
        document.getElementById("stop").addEventListener("click", evt => this.switchboard.stop());

        this.position_elm.addEventListener('input', this.user_adjusted_position.bind(this));


    }

    on_file_load(meta) {
        console.log("Song loaded: ", meta);
    }

    on_check_current_song(raw) {
        let response = JSON.parse(raw);

        if (response.status === true) {
            this.set_title(response.meta.title);
            this.set_artist(response.meta.artist);
            this.set_length(response.length.string);
        }

    }

    on_new_song(raw) {
        let data = JSON.parse(raw)
        console.log("There is a new song loaded", data.meta);
        this.set_title(data.meta.title);
        this.set_artist(data.meta.artist);
        this.set_length(data.length.string);

        this.song_length = data.length.seconds;
    }

    on_song_update(position, is_playing) {
        // TODO - this math is a tad hairy and I know there is a simpler equation
        let perc = 100 - (((this.song_length - position)/this.song_length) * 100)

        let seconds = Math.floor(position%60);
        let minutes = Math.floor(position/60);

        // https://stackoverflow.com/a/2998874/9908
        const zeroPad = (num, places) => String(num).padStart(2, '0');

        this.current_time_elm.innerHTML = zeroPad(minutes, 2) + ":" + zeroPad(seconds, 2);


        console.log("Song is @ ", perc, "and is playing:", is_playing);
        this.set_song_position(perc);

    }

    set_song_position(position){
        this.position_elm.value = position
    }

    set_title(title) {
        this.title_elm.innerHTML = title;
    }

    set_artist(artist) {
        this.artist_elm.innerHTML = artist;
    }

    set_length(length) {
        this.length_elm.innerHTML = length;
    }

}