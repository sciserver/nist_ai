window.myNamespace = Object.assign({}, window.myNamespace, {  
    mySubNamespace: {  
        pointToLayer: function(feature, latlng, context) {  
            return L.circleMarker(latlng)  
        },
        pointToLayer2: function(feature, latlng, context) {
            const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
            const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
            circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop.
            return L.circleMarker(latlng, circleOptions);  // sender a simple circle marker.
        }
    }  
});