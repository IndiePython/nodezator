"""Function for extending rectsman.main.RectsManager class."""


def get_clusters(self, *inflation):
    """Return clusters formed by close rects.

    Parameters
    ==========
    inflation (two integers or iterable containing them)
        amount of size to inflate each rect in order to
        check by collision whether they are close enough
        to be considered in the same cluster. This is
        the same as the argument(s) passed to
        pygame.Rect.inflate/inflate_ip
    """
    ### list objects
    rects = [rect for rect in self._get_all_rects()]

    ### create another list representing a cluster with
    ### a rect
    cluster = [rects.pop()]

    ### create a rectsman representing a rect of the
    ### whole cluster
    cluster_rect = self.__class__(cluster.__iter__)

    ### keep checking for collisions while there are still
    ### rects

    while rects:

        ## get an inflated version of the current
        ## cluster and check whether any rect from
        ## the list collides with it

        inflated = cluster_rect.inflate(*inflation)

        result = inflated.collidelist([rect for rect in rects])

        ## no collision;
        ##
        ## if no collision was detected, yield the
        ## rects in the cluster and change the cluster
        ## so it has only a new rect

        if result == -1:

            yield cluster[:]

            cluster[:] = [rects.pop()]

        ## collision detected;
        ##
        ## if a collision was detected, though, it
        ## means the rect which collided is part
        ## of the cluster, so we append it to the
        ## cluster
        else:
            cluster.append(rects.pop(result))

    ### if there's still rects in the cluster, yield it
    if cluster:
        yield cluster
