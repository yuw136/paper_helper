import React, { useEffect, useState } from "react";
import axios from "axios";
import { Button, Input, message } from "antd";

import {
  AudioOutlined,
  PauseOutlined,
  CaretRightOutlined,
  StopOutlined,
} from "@ant-design/icons";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
import Speech from "speak-tts";

const { Search } = Input;

const DOMAIN = "http://localhost:5001";

const searchContainer = {
  display: "flex",
  justifyContent: "center",
};

const ChatComponent = (props) => {
  const { handleResp, isLoading, setIsLoading } = props;
  const [searchValue, setSearchValue] = useState("");
  const [isChatModeOn, setIsChatModeOn] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [speech, setSpeech] = useState();
  const [pause, setPause] = useState(false);

  // speech recognation
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();

  useEffect(() => {
    const initializedSpeech = new Speech();
    initializedSpeech
      .init({
        volume: 1,
        lang: "en-US",
        rate: 1,
        pitch: 1,
        splitSentences: false,
        //just use default voice
      }) // return a Promise
      .then((data) => {
        console.log("Speech ready", data);
        setSpeech(initializedSpeech);
      })
      .catch((error) => {
        console.error("Failed to initialize speech:", error);
        // Try without specific voice
      });
  }, []);

  useEffect(() => {
    if (!listening && Boolean(transcript)) {
      (async () => await onSearch(transcript))();
      setIsRecording(false);
    }
  }, [listening, transcript]);

  const talk = (what2say) => {
    speech
      .speak({
        text: what2say,
        queue: false, // current speech will be interrupted
        listeners: {
          onstart: () => {
            console.log("Start utterance");
          },
          onend: () => {
            console.log("End utterance");
          },
          onresume: () => {
            console.log("Resume utterance");
          },
          onboundary: (event) => {
            // console.log(
            //   event.name +
            //     " boundary reached after " +
            //     event.elapsedTime +
            //     " milliseconds."
            // );
          },
        },
      })
      .then(() => {
        console.log("Success !");
        //userStartConvo();
      })
      .catch((e) => {
        console.error("An error occurred :", e);
      });
  };

  // const userStartConvo = () => {
  //   SpeechRecognition.startListening();
  //   setIsRecording(true);
  //   resetTranscript();
  // };

  const chatModeClickHandler = () => {
    setIsChatModeOn(!isChatModeOn);
    setIsRecording(false);
    SpeechRecognition.stopListening();
    resetTranscript();
  };

  const recordingClickHandler = () => {
    if (isRecording) {
      setIsRecording(false);
      SpeechRecognition.stopListening();
      resetTranscript();
    } else {
      setIsRecording(true);
      SpeechRecognition.startListening();
    }
  };

  const onSearch = async (question) => {
    setSearchValue("");
    setIsLoading(true);
    try {
      const response = await axios.get(`${DOMAIN}/chat`, {
        params: {
          question,
        },
      });
      handleResp(question, response.data);
      if (isChatModeOn) {
        talk("RAG Answer: " + response.data?.ragAnswer);
      }
    } catch (error) {
      //console.error("Chat error:", error);
      handleResp(question, {
        ragAnswer: "Error: " + error.message,
        mcpAnswer: "N/A",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setSearchValue(e.target.value);
  };

  const stopSpeech = () => {
    if (speech) {
      speech.cancel();
      console.log("Speech cancelled");
    }
  };

  const pauseOrResumeSpeech = () => {
    if (speech) {
      if (!pause) {
        speech.pause();
        setPause(true);
        console.log("Speech paused");
      } else {
        speech.resume();
        setPause(false);
        console.log("Speech resumed");
      }
    }
  };

  return (
    <div style={searchContainer}>
      {!isChatModeOn && (
        <Search
          placeholder="Ask a question about your document..."
          enterButton="Ask"
          size="large"
          onSearch={onSearch}
          loading={isLoading}
          value={searchValue}
          onChange={handleChange}
        />
      )}

      <Button
        type="primary"
        size="large"
        danger={isChatModeOn}
        onClick={chatModeClickHandler}
        style={{ marginLeft: "5px" }}
      >
        Chat Mode: {isChatModeOn ? "On" : "Off"}
      </Button>
      {isChatModeOn && (
        <Button
          type="primary"
          icon={<AudioOutlined />}
          size="large"
          danger={isRecording}
          onClick={recordingClickHandler}
          style={{ marginLeft: "5px" }}
        >
          {isRecording ? "Recording..." : "Click to record"}
        </Button>
      )}

      {isChatModeOn && (
        <>
          <Button
            type="default"
            size="large"
            onClick={pauseOrResumeSpeech}
            icon={pause ? <CaretRightOutlined /> : <PauseOutlined />}
            style={{ marginLeft: "5px" }}
          ></Button>

          <Button
            type="default"
            size="large"
            onClick={stopSpeech}
            style={{ marginLeft: "5px" }}
          >
            stop
          </Button>
        </>
      )}
    </div>
  );
};

export default ChatComponent;
