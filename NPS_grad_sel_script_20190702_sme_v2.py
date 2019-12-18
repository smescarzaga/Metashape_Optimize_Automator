# This following script was written by Stephen Escarzaga for the NPS AKRO Natural Resources SfM protocol pertaining to the gradual selection, error reduction
# and camera optimization steps. When ready to run this script, click on "Tools" in the top Metashape menu bar then click on "Run Script". Navigate to where the
# script is located and select it. While the script runs, pertinent information required by the current SfM protocol will be written
# to the Console window of Metashape, each line prefaced with "****". This includes # of starting points, # of points selected and removed during 
# each step and total camera error at each step. The script can be run within the document with multiple chunks and will only apply to the active
# chunk.

# Acknowledgements:
# This work is supported and monitored by The National Oceanic and Atmospheric Administration – Cooperative Science Center
# for Earth System Sciences and Remote Sensing Technologies (NOAA-CESSRST) under the Cooperative Agreement Grant # NA16SEC4810008.
# The author would like to thank The City College of New York, NOAA-CESSRST (aka CREST) program and NOAA Office of Education, 
# Educational Partnership Program for full fellowship support for Stephen M. Escarzaga. Thank you to Alexey Pasumansky of Agisoft LLC 
# for his assistance in the creation of this script.


# ***Save functions after each step in this script will throw an error if script is run on a document in 'view only' mode.

# - Stephen Escarzaga
# smescarzaga@utep.edu or smescarzaga@gmail.com

import Metashape, math, sys


doc = Metashape.app.document #specifies open document
chunk = doc.chunk #specifies active chunk
T = chunk.transform.matrix
crs = chunk.crs
pc = chunk.point_cloud #PointCloud object of sparse cloud points
pc_init = len(pc.points) #returns integer of number of sparse cloud points
print("****Number of starting points:", pc_init) #prints initial point number in raw sparse cloud

# Below starts the gradual selection, filtering and optimization process

#Reconstrution Uncertainty
threshold = 15 
f = Metashape.PointCloud.Filter()
f.init(pc, criterion = Metashape.PointCloud.Filter.ReconstructionUncertainty)
values = f.values.copy()
values.sort()
thresh = values[int(len(values) * (1-threshold/100))]
f.selectPoints(thresh)
nselected = len([p for p in pc.points if p.selected])
pc.removeSelectedPoints()
print("****", nselected, " points removed during reconstuction uncertainty filtering")
#Camera optimization
chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=False, fit_b2=False, fit_k1=True,
fit_k2=True, fit_k3=True, fit_k4=False, fit_p1=True, fit_p2=True, fit_p3=False,
fit_p4=False, adaptive_fitting=False, tiepoint_covariance=False)
#Report Total Camera Error
sums = 0
num = 0
for camera in chunk.cameras:
    if not camera.transform:
         continue
    if not camera.reference.location:
         continue

    estimated_geoc = chunk.transform.matrix.mulp(camera.center)
    error = chunk.crs.unproject(camera.reference.location) - estimated_geoc
    error = error.norm()
    sums += error**2
    num += 1
print("****Total Camera Error: ", round(math.sqrt(sums / num),3))
doc.save()

#Projection Accuracy
threshold = 15 
f = Metashape.PointCloud.Filter()
f.init(pc, criterion = Metashape.PointCloud.Filter.ProjectionAccuracy)
values = f.values.copy()
values.sort()
thresh = values[int(len(values) * (1-threshold/100))]
f.selectPoints(thresh)
nselected = len([p for p in pc.points if p.selected])
pc.removeSelectedPoints()
print("****", nselected, " points removed during projection accuracy filtering")
#Camera optimization
chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=False, fit_b2=False, fit_k1=True,
fit_k2=True, fit_k3=True, fit_k4=False, fit_p1=True, fit_p2=True, fit_p3=False,
fit_p4=False, adaptive_fitting=False, tiepoint_covariance=False)
#Report Total Camera Error
sums = 0
num = 0
for camera in chunk.cameras:
    if not camera.transform:
         continue
    if not camera.reference.location:
         continue

    estimated_geoc = chunk.transform.matrix.mulp(camera.center)
    error = chunk.crs.unproject(camera.reference.location) - estimated_geoc
    error = error.norm()
    sums += error**2
    num += 1
print("****Total Camera Error: ", round(math.sqrt(sums / num),3))
doc.save()

# Reprojection Error
# This step needs to be iterated until until camera accuracy reaches 20cm. Should
# sucessive iterations not decrease that number for some reason, this step will be
# limitted to 4 iterations.

for i in range(4):
	if (round(math.sqrt(sums / num),3)) <= 0.20:
		print('****Camera error has reached ~20cm')
		doc.save()
	else:
		threshold = 10
		f = Metashape.PointCloud.Filter()
		f.init(pc, criterion = Metashape.PointCloud.Filter.ReprojectionError)
		values = f.values.copy()
		values.sort()
		thresh = values[int(len(values) * (1-threshold/100))]
		f.selectPoints(thresh)
		nselected = len([p for p in pc.points if p.selected])
		pc.removeSelectedPoints()
		print("****", nselected, " points removed during reprojection error filtering")
		#Camera optimization
		chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_b1=True, fit_b2=True, fit_k1=True,
		fit_k2=True, fit_k3=True, fit_k4=True, fit_p1=True, fit_p2=True, fit_p3=True,
		fit_p4=True, adaptive_fitting=False, tiepoint_covariance=False)
		#Report Total Camera Error
		sums = 0
		num = 0
		for camera in chunk.cameras:
		    if not camera.transform:
		         continue
		    if not camera.reference.location:
		         continue

		    estimated_geoc = chunk.transform.matrix.mulp(camera.center)
		    error = chunk.crs.unproject(camera.reference.location) - estimated_geoc
		    error = error.norm()
		    sums += error**2
		    num += 1
		print("****Total Camera Error: ", round(math.sqrt(sums / num),3))
doc.save()






