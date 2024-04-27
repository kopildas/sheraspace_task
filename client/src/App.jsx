import { useState } from "react";
import { IoMdSend } from "react-icons/io";
import Skeleton_loader from "./components/Skeleton_loader";

function App() {
  const [loader, setLoader] = useState(false);
  const [answer, setAnswer] = useState(null);

  const [formData, setFormData] = useState({
    question: "",
  });
  const { question } = formData;

  const handleInputChange = (e) => {
    setFormData((prevState) => ({
      ...prevState,
      [e.target.id]: e.target.value,
    }));
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setAnswer(null);
    setLoader(true);

    fetch("https://sheraspace-task.onrender.com/api/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question }),
    })
      .then((response) => response.json())
      .then((data) => {
        setAnswer(data.answer);
        setLoader(false);
      })
      .catch((error) => {
        setAnswer(null);
        setLoader(false);
      });
  }


  return (
    <>
      <div className="flex flex-col items-center justify-center bg-black text-slate-100 h-screen">
        <form
          onSubmit={handleSubmit}
          className="w-[50%] bg-red-00 rounded-md relative"
        >
          <label className="mb-4 flex items-center">
            <input
              className="input-field w-full  focus:border-none px-4 py-4 rounded-2xl border-b-2 border-b-gray-400 bg-transparent mr-4"
              type="text"
              id="question"
              placeholder="Type and ask any question about interior design"
              value={question}
              onChange={handleInputChange}
            />
            <button
              className="bg-blue-00 text-2xl hover:text-4xl text-white font-medium uppercase hover:text-blue-400 transition-all duration-300 ease-in-out shadow-lg py-2 px-4 rounded-lg absolute right-0 mr-5"
              type="submit"
              disabled={loader}
            >
              <IoMdSend/>
            </button>
          </label>
        </form>

        {loader && <Skeleton_loader />}
        {answer && (
          <div className="w-[50%] px-5">
            <p className="text-blue-300">Answer:</p>
            {answer}
          </div>
        )}
      </div>
    </>
  );
}

export default App;
