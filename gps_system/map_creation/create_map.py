import cv2
import sys
import time
import xml.etree.ElementTree as ET
import xml.dom.minidom
import subprocess

sys.path.append('./')

class AppendNodes:

    def __init__(self, img, p1, p2, retreive=False) -> None:

        self.exit_flag = False
        self.H, self.W, _ = img.shape
        self.p1 = p1
        self.p2 = p2
        self.count_nodes = 0

        self.Xfactor = abs((p1['x'] - p2['x']) / self.W)
        self.Yfactor = abs((p1['y'] - p2['y']) / self.H)
        self.prev_node = {}
        self.cur_node = {}

        if not retreive:

            # Set the xmlns and xsi attributes
            self.root = ET.Element("graphml")
            self.root.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
            self.root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            self.root.set("xsi:schemaLocation", "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")

            # Create the key elements
            d0 = ET.SubElement(self.root, "key")
            d0.set("attr.name", "x")
            d0.set("attr.type", "double")
            d0.set("for", "node")
            d0.set("id", "d0")

            d1 = ET.SubElement(self.root, "key")
            d1.set("attr.name", "y")
            d1.set("attr.type", "double")
            d1.set("for", "node")
            d1.set("id", "d1")

            d2 = ET.SubElement(self.root, "key")
            d2.set("attr.name", "dotted")
            d2.set("attr.type", "boolean")
            d2.set("for", "edge")
            d2.set("id", "d2")

            # Create the graph element
            self.graph = ET.SubElement(self.root, "graph")
            self.graph.set("edgedefault", "directed")

        else:
            tree = ET.parse('lab_track_map.graphml')
            self.root = tree.getroot()
            self.graph = ET.SubElement(self.root, "graph")

        self.img = img
        cv2.imshow('track_image', self.img)
        cv2.moveWindow('track_image', 0, 0)
        result = subprocess.run(['wmctrl', '-r', 'track_image', '-b', 'toggle,above'])
        print(f'--> Set always on top: {result}')
        cv2.setMouseCallback('track_image', self.click_event)

    def pixel2coors(self, px, py):

        X_coor = round(px*self.Xfactor + self.p1['x'], 2)
        Y_coor = round(py*self.Yfactor + self.p1['y'], 2)

        save_node = input("Save node? [Y/n/E]")

        if save_node != 'n' and save_node != 'E':
        
            # Create the node element
            node = ET.SubElement(self.graph, "node")
            node.set("id", str(self.count_nodes))

            # Create the data elements
            x = ET.SubElement(node, "data")
            x.set("key", "d0")
            x.text = str(X_coor)

            y = ET.SubElement(node, "data")
            y.set("key", "d1")
            y.text = str(Y_coor)

            return X_coor, Y_coor, node

        elif save_node == 'n':
            mul_edges = input('Shall we find multiple edges? [Y/n]')
            if mul_edges == 'Y':
                self.mulEdges()
                cv2.imshow('track_image', self.img)
                cv2.imwrite('test_image.png', lab_track)
                
                # Prettify the XML
                xmlstr = xml.dom.minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")

                with open(f"lab_track_map.graphml", "w") as f:
                    f.write(xmlstr)
                print('------------------\n')
                sys.exit()
                
        elif save_node == 'E':
            sys.exit()

        return None, None, None

    def addEdge(self, source, target, dotted_flag=False):
        edge = ET.SubElement(self.graph, "edge")
        edge.set("source", source)
        edge.set("target", target)

        # Create the data element
        dotted = ET.SubElement(edge, "data")
        dotted.set("key", "d2")
        dotted.text = str(dotted_flag)

    def setEdges(self, dotted_flag):

        if len(all_nodes) > 1:

            source = str(all_nodes[-2]['node'].get("id"))
            target = str(all_nodes[-1]['node'].get("id"))
            self.addEdge(source, target, dotted_flag)

            return True
        return False

    def mulNodes(self):
        while True:
            copy_node_id = input(f'Add intersection nodes to copy: ')
            muls = input(f'Add number of copies: ')

            copy_node = self.root.find(f"./graph/node[@id='{copy_node_id}']")
            for data in copy_node.iter("data"):
                key = data.attrib["key"]
                value = data.text
                if key == 'd0':
                    X_copy = value
                elif key == 'd1':
                    Y_copy = value
                else:
                    print('Other key node found!')

            for _ in range(int(muls)):
                node = ET.SubElement(self.graph, "node")
                node.set("id", str(self.count_nodes))

                # Create the data elements
                x = ET.SubElement(node, "data")
                x.set("key", "d0")
                x.text = str(X_copy)

                y = ET.SubElement(node, "data")
                y.set("key", "d1")
                y.text = str(Y_copy)
                
                node_copy = {}
                for node_obj in all_nodes:
                    if node_obj['node'].get("id") == copy_node_id:
                        node_copy['px'] = node_obj['px']
                        node_copy['py'] = node_obj['py']

                node_copy['node'] = node
                all_nodes.append(node_copy)

                source_nodes = input(f'Add source nodes of intersection node = {self.count_nodes}: ')
                connections_ids = source_nodes.split()

                if len(connections_ids):
                    for connection in connections_ids:
                        source_node = self.root.find(f"./graph/node[@id='{connection}']")
                        source_id = source_node.get("id")
                        target_id = copy_node_id
                        self.addEdge(source_id, target_id)
                        self.add_arrowed_line(source_id, target_id)

                target_nodes = input(f'Add target nodes of intersection node = {self.count_nodes}: ')
                connections_ids = target_nodes.split()

                if len(connections_ids):
                    for connection in connections_ids:
                        target_node = self.root.find(f"./graph/node[@id='{connection}']")
                        target_id = target_node.get("id")
                        source_id = copy_node_id
                        self.addEdge(source_id, target_id)
                        self.add_arrowed_line(source_id, target_id)
                
                self.count_nodes += 1

            repeat = input('Add other intersection node copies [Y/n]? ')
            if repeat == 'n':
                break
            else:
                continue

    def mulEdges(self):
        for node in self.root.findall("./graph/node"):
            source_id = node.get("id")
            
            connections = input(f'Add target nodes for source_id = {source_id}: ')
            connections_ids = connections.split()

            if len(connections_ids):
                for connection in connections_ids:
                    target_node = self.root.find(f"./graph/node[@id='{connection}']")
                    target_id = target_node.get("id")
                    self.addEdge(source_id, target_id)

                    self.add_arrowed_line(source_id, target_id)

        add_copy_nodes = input('Shall we add some copy nodes [Y/n]? ')
        if add_copy_nodes == 'Y':
            self.mulNodes()

    def add_arrowed_line(self, source_id, target_id):
        pt1 = None
        pt2 = None
        for node in all_nodes:
            if node['node'].get("id") == source_id:
                pt1 = (node['px'], node['py'])
            if node['node'].get("id") == target_id:
                pt2 = (node['px'], node['py'])
            
            if pt1 and pt2:
                break

        cv2.arrowedLine(self.img, pt1, pt2,
                            color=(80, 200, 80), thickness=2, tipLength=0.2)

    def click_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:

            X_coor, Y_coor, node_ret = self.pixel2coors(x, y)

            if node_ret is not None:
                self.count_nodes += 1
                node = {}
                node['px'] = x
                node['py'] = y
                node['node'] = node_ret
                all_nodes.append(node)

                cv2.circle(self.img, (x, y), radius=5, color=(50, 200, 50), thickness=-1)
                cv2.putText(self.img, str(node['node'].get('id')), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 255, 255), 2)
                print(f"{x} and {y} pressed! | ({X_coor}, {Y_coor}) detected!")

                add_edge = input('Add edge? [Y/n/E]')
                if add_edge != 'n' and add_edge != 'E':
                    dotted = input('Dotted? [Y/n]')
                    if dotted == 'Y':
                        dotted_flag = True
                    else:
                        dotted_flag = False
                    
                    ret = self.setEdges(dotted_flag)
                    if ret:
                        pt1 = (all_nodes[-2]['px'], all_nodes[-2]['py'])
                        pt2 = (all_nodes[-1]['px'], all_nodes[-1]['py'])
                        cv2.arrowedLine(self.img, pt1, pt2,
                                            color=(80, 200, 80), thickness=2, tipLength=0.2)
                elif add_edge == 'E':
                    mul_edges = input('Shall we find multiple edges? [Y/n]')
                    if mul_edges == 'Y':
                        self.mulEdges()
                        self.exit_flag = True
                    else:
                        self.exit_flag = True

                cv2.imshow('track_image', self.img)
                cv2.imwrite('test_image.png', lab_track)
                
                # Prettify the XML
                xmlstr = xml.dom.minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")

                with open(f"lab_track_map.graphml", "w") as f:
                    f.write(xmlstr)
                print('------------------\n')
                if self.exit_flag:
                    sys.exit()

if __name__ == "__main__":

    lab_track = cv2.imread('LabTrack2023_grid_IRL_15cm.png')
    lab_track = cv2.resize(lab_track, dsize=None, fx=0.6, fy=0.6, interpolation=cv2.INTER_LINEAR)
    p1 = {
        'x': 0.48,
        'y': 0.18
    }
    p2 = {
        'x': 6.5,
        'y': 4.2
    }
    appender = AppendNodes(lab_track, p1, p2, retreive=False)
    all_nodes = []
    
    if cv2.waitKey(0) & 0xFF == ord('q'):      
        cv2.destroyAllWindows()