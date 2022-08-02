# NLP Transformer-Based Legalese Interpreter Demo1
 This is a service that queries a an NLP model pretrained on legal documents. It recognizes entities such as judges, courts, provisions, casenames, etc.  It also recognized sentences that it judges to be conclusions, issues, or axioms. 
 
 TO USE:
 1. Build the docker container using the included Dockerfile (ie, with the 'docker build' command)
 2. Run the docker container with port 5000 opened as port 5000.
 3. Open localhost on port 5000. Make sure it is HTTP (for the purposes of the demo). ie, http://localhost:5000 or http://{local ip here}:5000
 4. Upload a Word document. For the moment, only .docx files are accepted (for now. Broader file acceptance is an easy get)
 
 Results are at times inaccurate, in large part because the model is a prototype, and fine-tuning has been hard to do because of a lack of publicly available datasets (not an entire lack, but the gathering would not be a quick task). At the moment, the open-sourced Blackstone model from the Incorporated Council of Law Reporting for England and Wales' research lab, ICLR&D. is being utilized. The next step is to train/finetune a full size transformer model, for instance the 6-billion parameter GPT-J for the task. The only hindrance to this (and hence, the only reason the Blackstone model was chosen at all) is the collection of the training data. I have identified good sources for these, and have a training setup established for the task.
