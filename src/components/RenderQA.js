import React from "react";
import { Spin } from "antd";

const containerStyle = {
  display: "flex",
  justifyContent: "space-between",
  flexDirection: "column",
  marginBottom: "20px",
};

const userContainer = {
  textAlign: "right",
};

const agentContainer = {
  textAlign: "left",
};

const userStyle = {
  maxWidth: "50%",
  textAlign: "left",
  backgroundColor: "#1677FF",
  color: "white",
  display: "inline-block",
  borderRadius: "10px",
  padding: "10px",
  marginBottom: "10px",
};

const answerContainer = {
  marginBottom: "10px",
};

const answerLabel = {
  fontSize: "12px",
  fontWeight: "bold",
  color: "#666",
  marginBottom: "5px",
};

const ragAnswerStyle = {
  maxWidth: "50%",
  textAlign: "left",
  backgroundColor: "#E6F7FF",
  color: "black",
  display: "inline-block",
  borderRadius: "10px",
  padding: "10px",
  marginBottom: "5px",
  borderLeft: "4px solid #1890FF",
};

const mcpAnswerStyle = {
  maxWidth: "50%",
  textAlign: "left",
  backgroundColor: "#F6FFED",
  color: "black",
  display: "inline-block",
  borderRadius: "10px",
  padding: "10px",
  marginBottom: "5px",
  borderLeft: "4px solid #52C41A",
};

const RenderQA = (props) => {
  const { conversation, isLoading } = props;

  return (
    <>
      {conversation?.map((each, index) => {
        return (
          <div key={index} style={containerStyle}>
            <div style={userContainer}>
              <div style={userStyle}>{each.question}</div>
            </div>
            <div style={agentContainer}>
              <div>
                <div style={answerContainer}>
                  <div style={answerLabel}>RAG Answer (from document):</div>
                  <div style={ragAnswerStyle}>{each.answer.ragAnswer}</div>
                </div>
                <div style={answerContainer}>
                  <div style={answerLabel}>MCP Answer (with web search):</div>
                  <div style={mcpAnswerStyle}>{each.answer.mcpAnswer}</div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
      {isLoading && <Spin size="large" style={{ margin: "10px" }} />}
    </>
  );
};

export default RenderQA;
