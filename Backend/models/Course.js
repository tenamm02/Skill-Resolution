const courseSchema = new mongoose.Schema({
    title: String,
    description: String,
    content: String,
    creator: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }
 });
 
 module.exports = mongoose.model('Course', courseSchema);
 