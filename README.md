# NLP Transformer-Based Legalese Interpreter Demo1
 This is a service that queries a transformer-based NLP model pretrained on legal documents. It recognized entities such as judges, courts, provisions, casenames, etc.  It also recognized sentences that it judges to be conclusions, issues, or axioms. 
 
 TO USE:
 1. Build the docker container using the included Dockerfile (ie, with the 'docker build' command)
 2. Open localhost on port 5000. Make sure it is HTTP (for the purposes of the demo). ie, http://localhost:5000 or http://{local ip here}:5000
