import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:google_maps_flutter/google_maps_flutter.dart';

void main() {
  runApp(SanpoApp());
}

class SanpoApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: SanpoHome(),
    );
  }
}

class SanpoHome extends StatefulWidget {
  @override
  _SanpoHomeState createState() => _SanpoHomeState();
}

class _SanpoHomeState extends State<SanpoHome> {
  GoogleMapController? mapController;
  Set<Polyline> polylines = {};

  final originController = TextEditingController();
  final destinationController = TextEditingController();

  Future<void> fetchRoute() async {
    final origin = originController.text;
    final destination = destinationController.text;

    final url = Uri.parse(
        "http://10.0.2.2:8000/search?origin=$origin&destination=$destination&mode=high");

    final response = await http.get(url);
    final data = jsonDecode(response.body);

    List coords = data["route"]; // [[lat, lng], [lat, lng], ...]

    List<LatLng> latlngs = coords
        .map((c) => LatLng(c[0].toDouble(), c[1].toDouble()))
        .toList();

    setState(() {
      polylines = {
        Polyline(
          polylineId: PolylineId("route"),
          color: Colors.blue,
          width: 5,
          points: latlngs,
        )
      };
    });

    if (latlngs.isNotEmpty) {
      mapController?.animateCamera(
        CameraUpdate.newLatLngZoom(latlngs[0], 14),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Sanpo Flutter版")),
      body: Column(
        children: [
          TextField(
            controller: originController,
            decoration: InputDecoration(labelText: "出発地"),
          ),
          TextField(
            controller: destinationController,
            decoration: InputDecoration(labelText: "目的地"),
          ),
          ElevatedButton(
            onPressed: fetchRoute,
            child: Text("検索"),
          ),
          Expanded(
            child: GoogleMap(
              onMapCreated: (c) => mapController = c,
              initialCameraPosition: CameraPosition(
                target: LatLng(35.6812, 139.7671),
                zoom: 13,
              ),
              polylines: polylines,
            ),
          )
        ],
      ),
    );
  }
}
