#include <faunus/faunus.h>
#include<iostream>
#include<fstream>

using namespace Faunus;
using namespace Faunus::Potential;

//typedef Space<Geometry::Cuboid> Tspace;
typedef Space<Geometry::PeriodicCylinder> Tspace;
typedef CombinedPairPotential< DebyeHuckel, LennardJonesLB > Tpairpot;

//int file_counter = 0;

int main(int argc, char** argv) {
    InputMap mcp("hsa.json");
    FormatXTC xtc(1000);                 // XTC gromacs trajectory format
    EnergyDrift sys;                     // class for tracking system energy drifts

    Tspace spc(mcp);
    auto pot = Energy::Nonbonded<Tspace,Tpairpot>(mcp)
        + Energy::EquilibriumEnergy<Tspace>(mcp)
        + Energy::MassCenterConstrain<Tspace>(mcp, spc);

    Analysis::LineDistribution<> rdf(0.2);
    Analysis::ChargeMultipole mpol;
    //Analysis::MultipoleDistribution<Tspace> mpd(mcp);
    Analysis::CombinedAnalysis analysis(mcp, pot, spc);

    pot.first.first.pairpot.second.customParameters(mcp["customlj"]);

    spc.load("state"); // load previous state, if any

    Move::Propagator<Tspace> mv(mcp,pot,spc);

    sys.init( Energy::systemEnergy(spc,pot,spc.p) );    // Store total system energy

    cout << atom.info() << spc.info() << pot.info() << textio::header("MC Simulation Begins!");

  
    /*float thr = 3.0;           //Threshold for contact                                                                            
    int n=spc.p.size();        //Number of atoms    
    int t[n/2][n/2];           //Create table of residues combinations                                                                  
    for (int k = 0; k < n/2; k++ ) {       //Initialize table with zeroes                                                                 
       for ( int l = 0; l < n/2; l++ ) {   
          t[k][l] = 0;                           
        }
    }

    cout << "n equals:" << n << endl;*/

    MCLoop loop(mcp);
    while ( loop[0] ) {
        while ( loop[1] ) {
            sys += mv.move();

            analysis.sample();

            /*if (slump()>0.999995) {   
                file_counter++;
                std::string pqrname="pqr_"+std::to_string(file_counter)+".pqr";
                FormatPQR::save(pqrname, spc.p, spc.geo.len);
            }*/

            //mpd.sample( spc, *spc.groupList()[0], *spc.groupList()[1] );
            rdf( spc.geo.dist( spc.groupList()[0]->cm, spc.groupList()[1]->cm ))++;

            for (auto i : spc.groupList())
                mpol.sample(*i, spc);                              

            //if (slump()>0.99999) {                          //Trajectory saving
              //xtc.setbox( spc.geo.len );
              //xtc.save("traj.xtc", spc.p);
            //}


            /*if (slump()>0.999) {
                std::ofstream out("table.txt");           //File to save table
                for (int i = 0; i < n/2; i++ ) {          //Loop in protein 1
                    for ( int j = n/2; j < n; j++ ) {     //Loop in protein 2
                        float r2 = spc.geo.sqdist(spc.p[i],spc.p[j]);
                        float thr_tot = thr + spc.p[i].radius + spc.p[j].radius;
                        float thr_tot2 = pow(thr_tot,2);
                        int j_norm = j - n/2 ;            //Column number norm.
                        if ( r2 <= thr_tot2 ) {
                            int a = t[i][j_norm];
                            //cout << "a equals:" << a << endl;
                            t[i][j_norm] = a+1;           //Add 1 to cell 
                           }                
                        if ( t[i][j_norm] != 0 )          //Only print cells > 0
                          out << i << "\t" << j_norm << "\t" << t[i][j_norm] << "\n";
                  }
               }
                out.close();
            }*/


        } // end of micro loop

        sys.checkDrift( Energy::systemEnergy(spc,pot,spc.p) ); // detect energy drift

        cout << loop.timing();
        rdf.save("rdf.dat");
        FormatPQR::save("confout.pqr", spc.p, spc.geo.len);
        //FormatAAM::save("struct_cm.aam", spc.p);
        spc.save("state");
        //mpd.save("multipole.dat");

    } // end of macro loop

    //for (int a = 0; a < n/2 - 1; a++ ) {
        //for ( int b = n/2; b < n; b++ ) {
            //out << t[a][b] << endl;
        //}
    //}
    
    //out.close();

    cout << loop.info() + sys.info() + mv.info() + mpol.info() << endl;

}


/**
 * @page example_twobody Example: Osmotic Second Virial Coefficient
 *
 * In this example we calculate the potential of mean force between
 * two rigid bodies with a fluctuating charge distribution. Salt and
 * solvent are implicitly treated using a Debye-Huckel potential and
 * the rigid bodies (here proteins) are kept on a line and allowed to
 * translate, rotate, and protons are kept in equilibrium with bulk
 * using particle swap moves.
 *
 * During simulation we simply sample the probability of observing
 * the two bodies at a specific separation
 * (using `Faunus::Analysis::LineDistribution`).
 * As the proteins are confined onto a line, each volume element along
 * `r` is constant and there's thus no need to normalize with a spherical
 * shell as done for freely moving particles.
 * The minimum and maximum allowed distance between the two bodies can
 * specified via the `Faunus::Energy::MassCenterConstrain` term in the
 * Hamiltonian.
 *
 * ![Two rigid molecules kept on a line inside a periodic cylinder](twobody.png)
 *
 * Run this example from the `examples` directory:
 * The python script `twobody.py` generates the simulation input files
 * and all changes to the simulation setup should be done from inside
 * the script.
 * This example can run with the following (the first, optional
 * command checks out a specific commit with which this tutorial was created),
 *
 * ~~~~~~~~~~~~~~~~~~~
 * $ (git checkout 10e9a0b)
 * $ make example_twobody
 * $ cd src/examples
 * $ python twobody.py
 * ~~~~~~~~~~~~~~~~~~~
 *
 * For calculating the virial coefficient, @f$B_2@f$, the angularly averaged
 * radial distribution function, g(r), must be integrated according to,
 *
 * @f[ B_2 = -2\pi \int_0^{\infty} [ g(r) -1 ] r^2 dr @f]
 *
 * where it should be noted that noise at large separations is strongly
 * amplified. To fix this, the tail of the g(r) can be fitted to
 * a Yukawa potential of the form (see [doi:10/xqw](http://dx.doi.org/10/xqw)),
 *
 * @f[ w(r)/k_BT = -\ln g(r) = \lambda_B s^2 z_iz_j / r \exp{(-\kappa r )}  @f]
 *
 * where @f$ s=\sinh{(a\kappa)}/a\kappa @f$ scales the charges due to spreading
 * them over a sphere with effective radius, `a`.
 * The fitting can be done using the supplied python script `twobody.virial.py` which
 * require information about protein charges, fitting range, and Debye length.
 * Edit and run with,
 *
 * ~~~~
 * $ python twobody.virial.py
 * ~~~~
 * (requires `scipy` and `matplotlib`)
 *
 * The output could look like below, and it is important to ensure
 * that the fitted parameters (Debye length or effective radius or both)
 * are in the vicinity of the simulated system.
 * Note that in the
 * limit @f$ a\kappa \rightarrow 0 @f$, i.e. when the Debye length
 * is much bigger then the particle size, @f$ s \rightarrow 1 @f$
 * and fitting via the effective radius, @f$ a @f$, is unfeasible
 * and should be disabled in the script.
 * 
 * ~~~~
 * Excecuting python script to analyse the virial coeffient...
 * Loaded g(r) file      =  rdf.dat
 * Saved w(r) file       =  wofr.dat
* Particle charges      =  [7.1, 7.1]
* Particle weights      =  [6520.0, 6520.0] g/mol
* Fit range [rmin,rmax] =  40.0 90.0 A
* Fitted Debye length   =  12.1634707424 A
* Fitted ionic strength =  62.4643374077 mM
* Fitted radius         =  14.4531689553 A
* Virial coefficient (cubic angstrom):
    * Hard sphere  [    0:   19] =  14365.4560073
      * Loaded data  [   19:   40] =  72438.2668732
      * Debye-Huckel [   40:  500] =  74969.9046117
      * TOTAL        [    0:  500] =  161773.627492 A^3
      *                            =  0.0229167635392 ml*mol/g^2
      * Reduced, B2/B2_HS          =  11.2612942749
      * ~~~~
      *
      * If `matplotlib` is installed, the python script will offer to
      * visualize the fit.
    *
     * ![Fitting of the PMF tail to a Yukawa potential](twobody-plot.png)
      *
      * twobody.cpp
      * ===========
      * This is the underlying C++ program where one should note that the
      * pair potential is hard coded but can naturally be customised to
      * any potential from namespace `Faunus::Potential`.
      *
      * @includelineno examples/twobody.cpp
      */
