# LitLink

EE6008 AY24S1-44@MLDA

# System Main Function Description

## 1. PDF Upload and Management

Our system is equipped with a simple and easy-to-use upload interface that allows users to effortlessly upload PDF documents to the platform. Whether you click on the upload area or drag and drop the document, the upload process is extremely convenient. While the document is being uploaded, the system prompts the user to fill in necessary metadata such as the document title, description, and abstract. To improve efficiency, we utilize a carefully tuned large-scale language model for intelligent metadata auto-population, with pre-populated field content available for user review and modification. If a user cancels an upload, the system automatically deletes the relevant document record.

Additionally, users can search for uploaded documents by keyword and have the right to edit any part of the metadata, including the title, description, or abstract. Users can also remove documents they no longer need or access the learning interface for in-depth research and interaction.

## 2. Document Study Interface

In the document learning interface, the content of the PDF document is clearly displayed on the left side of the screen, while the right side contains cards, group chat, and other auxiliary tools to enhance the learning experience. As the core of learning, each card contains the document title, key text, learning status, AI analysis results, user notes, and related card links, which greatly facilitates users’ understanding and memorization of key knowledge.

## 3. Highlighting Capabilities

Our system offers both automatic and manual text highlighting options. When the AI auto-generation feature is enabled, the LitLink model automatically analyzes the document and flags key passages, while generating pull tabs containing AI insights. Users can also manually select text to highlight, and the system will create corresponding pull tabs accordingly. Each card is embedded in a vector space, allowing for quick retrieval of similar content and effective linking of knowledge points.

## 4. Group Chat with AI Agents

The Group Chat feature integrates several specialized AI agents, each built on a large language model that focuses on a different area of expertise. These agents include virtual document authors, LitLink models, web search assistants, and programming assistants that work together to provide comprehensive and coherent responses by sharing contextual information. The group chat also features a "dive mode" that allows users to deepen their understanding of the topic of discussion by observing the AI agent as a bystander in an autonomous discussion.
