// main44.cc is a part of the PYTHIA event generator.
// Copyright (C) 2022 Torbjorn Sjostrand.
// PYTHIA is licenced under the GNU GPL v2 or later, see COPYING for details.
// Please respect the MCnet Guidelines, see GUIDELINES for details.

// Author: Stefan Prestel <stefan.prestel@thep.lu.se>.

// Keywords: LHE file; hepmc;

// This program (main44.cc) illustrates how a file with HepMC2 events can be
// generated by Pythia8. See main45.cc for how to ouput HepMC3 events instead.
// Note: both main44.cc and main45.cc can use the same main44.cmnd input card.

#include "Pythia8/Pythia.h"
#ifndef HEPMC2
#include "Pythia8Plugins/HepMC3.h"
#else
#include "Pythia8Plugins/HepMC2.h"
#endif
#include <unistd.h>

using namespace Pythia8;

//==========================================================================

// Example main programm to illustrate merging.

int main( int argc, char* argv[] ){

  // Check that correct number of command-line arguments
  if (argc != 3) {
    cerr << " Unexpected number of command-line arguments ("<<argc<<"). \n"
         << " You are expected to provide the arguments" << endl
         << " 1. Input file for settings" << endl
         << " 2. Output file for HepMC events" << endl
         << " Program stopped. " << endl;
    return 1;
  }

  Pythia pythia;

  // Input parameters:
  pythia.readFile(argv[1],0);

  // Interface for conversion from Pythia8::Event to HepMC one.
  // Specify file where HepMC events will be stored.
  Pythia8ToHepMC ToHepMC(argv[2]);

  // Allow abort of run if many errors.
  int  nAbort  = pythia.mode("Main:timesAllowErrors");
  int  iAbort  = 0;
  bool doAbort = false;

  cout << endl << endl << endl;
  cout << "Start generating events" << endl;

  long nEvent = pythia.settings.mode("Main:numberOfEvents");
  int nRuns = pythia.mode("Main:numberOfSubruns");

  double sigmaTotal(0.), errorTotal(0.);

  // Loop over subruns with varying number of jets.
  for (int iRuns = 0; iRuns < nRuns; ++iRuns) {

    double sigmaSample = 0., errorSample = 0.;

    // Read in name of LHE file for current subrun and initialize.
    pythia.readFile(argv[1], iRuns);

    // Initialise.
    pythia.init();

    // Get the inclusive x-section by summing over all process x-sections.
    double xs = 0.;
    for (int i=0; i < pythia.info.nProcessesLHEF(); ++i)
      xs += pythia.info.sigmaLHEF(i);

    // Start generation loop
    while( pythia.info.nSelected() < nEvent ){

      // Generate next event
      if( !pythia.next() ) {
        if ( pythia.info.atEndOfFile() ) break;
        else if (++iAbort > nAbort) {doAbort = true; break;}
        else continue;
      }

      // Get event weight(s).
      double evtweight         = pythia.info.weight();

      // Do not print zero-weight events.
      if ( evtweight == 0. ) continue;

      // Work with weighted (LHA strategy=-4) events.
      double normhepmc = 1.;
      if (abs(pythia.info.lhaStrategy()) == 4)
        normhepmc = 1. / double(1e9*nEvent);
      // Work with unweighted events.
      else
        normhepmc = xs / double(1e9*nEvent);

      // Set event weight
      //hepmcevt.weights().push_back(evtweight*normhepmc);
      // Fill HepMC event
      ToHepMC.fillNextEvent( pythia );
      // Add the weight of the current event to the cross section.
      sigmaTotal  += evtweight*normhepmc;
      sigmaSample += evtweight*normhepmc;
      errorTotal  += pow2(evtweight*normhepmc);
      errorSample += pow2(evtweight*normhepmc);
      // Report cross section to hepmc
      ToHepMC.setXSec( sigmaTotal*1e9, pythia.info.sigmaErr()*1e9 );
      // Write the HepMC event to file. Done with it.
      ToHepMC.writeEvent();

    } // end loop over events to generate.
    if (doAbort) break;

    // print cross section, errors
    pythia.stat();

    cout << endl << " Contribution of sample " << iRuns
         << " to the inclusive cross section : "
         << scientific << setprecision(8)
         << sigmaSample << "  +-  " << sqrt(errorSample)  << endl;

  }

  cout << endl << endl << endl;
  if (doAbort)
    cout << " Run was not completed owing to too many aborted events" << endl;
  cout << endl << endl << endl;

  // Done
  return 0;

}
