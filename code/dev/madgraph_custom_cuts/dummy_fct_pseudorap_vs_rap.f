      logical FUNCTION dummy_cuts(P)
C**************************************************************************
C     INPUT:
C            P(0:3,1)           MOMENTUM OF INCOMING PARTON
C            P(0:3,2)           MOMENTUM OF INCOMING PARTON
C            P(0:3,3)           MOMENTUM OF ...
C            ALL MOMENTA ARE IN THE REST FRAME!!
C            COMMON/JETCUTS/   CUTS ON JETS
C     OUTPUT:
C            TRUE IF EVENTS PASSES ALL CUTS LISTED
C**************************************************************************
      IMPLICIT NONE
c
c     Constants
c
      include 'genps.inc'
      include 'nexternal.inc'

      REAL*8 pt, PtDot
      external pt, PtDot

      double precision eta, DELTA_PHI, delta_eta, r2_pseudo
      external eta, DELTA_PHI


      REAL*8 R2
      external R2
C       double precision r2(nincoming+1:nexternal,nincoming+1:nexternal)
C
C     ARGUMENTS
C
      REAL*8 P(0:3,nexternal)
C
C     PARAMETERS
C
      real*8 PI
      parameter( PI = 3.14159265358979323846d0 )
c
c     particle identification
c
      LOGICAL  IS_A_J(NEXTERNAL),IS_A_L(NEXTERNAL)
      LOGICAL  IS_A_B(NEXTERNAL),IS_A_A(NEXTERNAL),IS_A_ONIUM(NEXTERNAL)
      LOGICAL  IS_A_NU(NEXTERNAL),IS_HEAVY(NEXTERNAL)
      logical  do_cuts(nexternal)
      COMMON /TO_SPECISA/IS_A_J,IS_A_A,IS_A_L,IS_A_B,IS_A_NU,IS_HEAVY,
     . IS_A_ONIUM, do_cuts

      dummy_cuts=.true.

C       debug

C       if (pt(p(0,6)) .lt. 150d0) then
C             dummy_cuts=.false.
C       endif
      
C       if (dsqrt(r2(p(0,5),p(0,6))) .gt. 2d0) then
C             dummy_cuts=.false.
C       endif

C       if (PtDot(p(0,3), p(0,4)) .gt. 250.0d0**2) then
C             dummy_cuts=.false.
C       endif

C       if (dsqrt(r2(p(0,5),p(0,6))) .gt. 1.2d0) then
C             dummy_cuts=.false.
C       endif

C       if (abs(rap(p(0,5))-rap(p(0,6))) .lt. 1.0d0) then 
C             dummy_cuts=.false.
C       endif

C       ATLAS ZH -> bb conditional cuts

      if (PtDot(p(0,3),p(0,4)) .lt. 150.0d0**2) then
            if (dsqrt(r2(p(0,5),p(0,6))) .gt. 3.0d0) then
                  dummy_cuts=.false.
            endif
      else if (PtDot(p(0,3),p(0,4)) .lt. 200.0d0**2 .and. PtDot(p(0,3),p(0,4)) .ge. 150.0d0**2) then
            if (dsqrt(r2(p(0,5),p(0,6))) .gt. 1.8d0) then
                  dummy_cuts=.false.
            endif
      else
            if (dsqrt(r2(p(0,5),p(0,6))) .gt. 1.2d0) then
                  dummy_cuts=.false.
            endif
      endif
      
C       delta_eta = eta(p(0,5)) - eta(p(0,6))
C       r2_pseudo = DELTA_PHI(p(0,5),p(0,6))**2.0d0 + delta_eta**2.0d0

C       if (dsqrt(r2_pseudo).gt. 1.5d0) then
C             dummy_cuts=.false.
C       endif

C     delta phi cut works
C       if (dsqrt(DELTA_PHI(p(0,5),p(0,6))**2).gt. 1.0d0) then
C             dummy_cuts=.false.
C       endif

C     delta eta cut works
C       if (dsqrt(delta_eta**2).gt. 2.0d0) then
C             dummy_cuts=.false.
C       endif
      
      if ((dsqrt(delta_eta**2.0d0))**2.0d0 .gt.2.0d0) then
            dummy_cuts=.false.
      endif

C       if ((delta_eta**2.0d0).gt.2.0d0) then
C             dummy_cuts=.false.
C       endif




C       if (PtDot(p(0,3),p(0,4)) .lt. 150.0d0**2) then
C             if (dsqrt(r2_pseudo) .gt. 3.0d0) then
C                   dummy_cuts=.false.
C             endif
C       else if (PtDot(p(0,3),p(0,4)) .lt. 200.0d0**2 .and. PtDot(p(0,3),p(0,4)) .ge. 150.0d0**2) then
C             if (dsqrt(r2_pseudo) .gt. 1.8d0) then
C                   dummy_cuts=.false.
C             endif
C       else
C             if (dsqrt(r2_pseudo) .gt. 1.2d0) then
C                   dummy_cuts=.false.
C             endif
C       endif

      return
      end

      subroutine get_dummy_x1(sjac, X1, R, pbeam1, pbeam2, stot, shat)
      implicit none
      include 'maxparticles.inc'
      include 'run.inc'
c      include 'genps.inc'
      double precision sjac ! jacobian. should be updated not reinit
      double precision X1   ! bjorken X. output
      double precision R    ! random value after grid transfrormation. between 0 and 1
      double precision pbeam1(0:3) ! momentum of the first beam (input and/or output)
      double precision pbeam2(0:3) ! momentum of the second beam (input and/or output)
      double precision stot        ! total energy  (input and /or output)
      double precision shat        ! output

c     global variable to set (or not)
      double precision cm_rap
      logical set_cm_rap
      common/to_cm_rap/set_cm_rap,cm_rap
      
      set_cm_rap=.false. ! then cm_rap will be set as .5d0*dlog(xbk(1)*ebeam(1)/(xbk(2)*ebeam(2)))
                         ! ebeam(1) and ebeam(2) are defined here thanks to 'run.inc'
      shat = x1*ebeam(1)*ebeam(2)
      return 
      end

      subroutine get_dummy_x1_x2(sjac, X, R, pbeam1, pbeam2, stot,shat)
      implicit none
      include 'maxparticles.inc'
      include 'run.inc'
c      include 'genps.inc'
      double precision sjac ! jacobian. should be updated not reinit
      double precision X(2)   ! bjorken X. output
      double precision R(2)    ! random value after grid transfrormation. between 0 and 1
      double precision pbeam1(0:3) ! momentum of the first beam
      double precision pbeam2(0:3) ! momentum of the second beam
      double precision stot        ! total energy
      double precision shat        ! output

c     global variable to set (or not)
      double precision cm_rap
      logical set_cm_rap
      common/to_cm_rap/set_cm_rap,cm_rap
      
      set_cm_rap=.false. ! then cm_rap will be set as .5d0*dlog(xbk(1)*ebeam(1)/(xbk(2)*ebeam(2)))
                         ! ebeam(1) and ebeam(2) are defined here thanks to 'run.inc'
      shat = x(1)*x(2)*ebeam(1)*ebeam(2)
      return 
      end


      logical  function dummy_boostframe()
      implicit none
c
c      
      dummy_boostframe = .false.
      return
      end
      
